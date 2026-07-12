from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={'class': 'w-full pl-3 pr-9 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:outline-none text-sm transition-all'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full pl-11 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': 'Choose a username'}),
            'email': forms.EmailInput(attrs={'class': 'w-full pl-11 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': 'you@company.com'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full pl-3 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': 'John'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full pl-3 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': 'Doe'}),
            'phone': forms.TextInput(attrs={'class': 'w-full pl-11 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': '+1-555-0000'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'w-full pl-11 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': 'Create a strong password'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full pl-11 pr-4 py-2.5 bg-surface-container-low dark:bg-white/5 dark:text-white border border-outline-variant/30 dark:border-white/10 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary/30 focus:outline-none text-sm placeholder-outline transition-all', 'placeholder': 'Confirm your password'})
