from django import forms
from .models import Testimonial


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Your name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'you@domain.com'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Tell me about your project',
        'rows': 6
    }))
    attachment = forms.FileField(required=False, help_text='Optional: attach a brief/spec (max 5MB, PDF or image)',
        widget=forms.ClearableFileInput(attrs={'accept': '.pdf,image/*'}))
    # Keep optional on server to avoid breaking existing tests; enforced by light client-side validation
    privacy_agree = forms.BooleanField(required=False, label='I agree to the Privacy Policy')
    # honeypot: should remain empty
    hp = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_hp(self):
        data = self.cleaned_data.get('hp')
        if data:
            raise forms.ValidationError('Spam detected')
        return data

    def clean_attachment(self):
        f = self.cleaned_data.get('attachment')
        if not f:
            return f
        max_mb = 5
        if f.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f'File too large (>{max_mb}MB)')
        valid_mimes = {'application/pdf', 'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
        content_type = getattr(f, 'content_type', None)
        if content_type and content_type not in valid_mimes:
            raise forms.ValidationError('Unsupported file type. Please upload a PDF or image.')
        return f


class SubscribeForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'you@domain.com'
    }))
    hp = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean_hp(self):
        data = self.cleaned_data.get('hp')
        if data:
            raise forms.ValidationError('Spam detected')
        return data


class TestimonialForm(forms.ModelForm):
    hp = forms.CharField(required=False, widget=forms.HiddenInput)
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'you@company.com'}))

    class Meta:
        model = Testimonial
        fields = ['name','role','email','content','image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Share your experience working with me'}),
        }

    def clean_hp(self):
        data = self.cleaned_data.get('hp')
        if data:
            raise forms.ValidationError('Spam detected')
        return data
