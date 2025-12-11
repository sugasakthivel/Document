from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import FileResponse
from django.utils import timezone
from django.db.models import Count, Q
from .models import SharedFile, DownloadLog
from .forms import FileUploadForm, UserRegistrationForm
from django.contrib.auth import logout
from django.shortcuts import redirect

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    files = SharedFile.objects.filter(user=request.user)
    
    stats = {
        'total_files': files.count(),
        'active_files': files.filter(is_active=True, expires_at__gt=timezone.now()).count(),
        'expired_files': files.filter(Q(expires_at__lte=timezone.now()) | Q(is_active=False)).count(),
        'total_downloads': sum(f.download_count for f in files),
    }
    
    return render(request, 'dashboard.html', {'files': files, 'stats': stats})

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            shared_file = form.save(commit=False)
            shared_file.user = request.user
            shared_file.original_filename = request.FILES['file'].name
            shared_file.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('file_detail', token=shared_file.token)
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def file_detail(request, token):
    shared_file = get_object_or_404(SharedFile, token=token, user=request.user)
    download_logs = shared_file.downloads.all()[:20]
    download_url = request.build_absolute_uri(f'/download/{shared_file.token}/')
    
    return render(request, 'file_detail.html', {
        'file': shared_file,
        'download_logs': download_logs,
        'download_url': download_url
    })

@login_required
def delete_file(request, token):
    shared_file = get_object_or_404(SharedFile, token=token, user=request.user)
    if request.method == 'POST':
        shared_file.delete()
        messages.success(request, 'File deleted successfully!')
        return redirect('dashboard')
    return render(request, 'delete_confirm.html', {'file': shared_file})

@login_required
def toggle_file_status(request, token):
    shared_file = get_object_or_404(SharedFile, token=token, user=request.user)
    shared_file.is_active = not shared_file.is_active
    shared_file.save()
    status = 'activated' if shared_file.is_active else 'deactivated'
    messages.success(request, f'File {status} successfully!')
    return redirect('file_detail', token=token)

def download_file(request, token):
    shared_file = get_object_or_404(SharedFile, token=token)
    
    if not shared_file.can_download():
        return render(request, 'download_error.html', {
            'error': 'This link has expired or reached its download limit.'
        })
    
    try:
        response = FileResponse(
            shared_file.file.open('rb'), 
            as_attachment=True, 
            filename=shared_file.original_filename
        )
        
        DownloadLog.objects.create(
            shared_file=shared_file,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            success=True
        )
        
        shared_file.download_count += 1
        shared_file.save(update_fields=['download_count'])
        
        return response
    except Exception as e:
        DownloadLog.objects.create(
            shared_file=shared_file,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            success=False
        )
        return render(request, 'download_error.html', {
            'error': f'Error downloading file: {str(e)}'
        })

def logout_user(request):
    logout(request)
    return redirect('home')