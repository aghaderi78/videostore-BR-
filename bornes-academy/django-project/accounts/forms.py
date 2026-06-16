from django import forms
from .models import User


class SendOTPForm(forms.Form):
    mobile = forms.CharField(
        max_length=11,
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '09xxxxxxxxx',
            'dir': 'ltr',
            'autocomplete': 'tel',
        })
    )

    def clean_mobile(self):
        mobile = self.cleaned_data['mobile'].strip()
        if not mobile.startswith('09') or not mobile.isdigit() or len(mobile) != 11:
            raise forms.ValidationError('شماره موبایل معتبر نیست. مثال: 09123456789')
        return mobile


class VerifyOTPForm(forms.Form):
    mobile = forms.CharField(widget=forms.HiddenInput())
    code = forms.CharField(
        max_length=6,
        label='کد تأیید',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center',
            'placeholder': '------',
            'dir': 'ltr',
            'maxlength': '6',
            'autocomplete': 'one-time-code',
        })
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        if not code.isdigit() or len(code) != 6:
            raise forms.ValidationError('کد تأیید باید ۶ رقم عددی باشد')
        return code


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'نام',
            'last_name': 'نام خانوادگی',
            'email': 'ایمیل',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }
