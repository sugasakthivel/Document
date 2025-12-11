from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SharedFile

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = ['file', 'description', 'expiry_hours', 'max_downloads']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description...'
            }),
            'expiry_hours': forms.Select(attrs={'class': 'form-select'}),
            'max_downloads': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': '0 = unlimited'
            }),
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
