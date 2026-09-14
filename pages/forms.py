from django import forms
from .models import ContactMessage

LOOKING_TO_CHOICES = [
    ('', 'Select an option'),
    ('buy', 'Buy'),
    ('sell', 'Sell'),
    ('rent', 'Rent / Lease'),
    ('invest', 'Invest'),
    ('explore', 'Just exploring'),
]


class ContactForm(forms.ModelForm):
    looking_to = forms.ChoiceField(
        choices=LOOKING_TO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    location_preference = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Kollam, Kerala'}),
    )
    budget = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50,00,000'}),
    )
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'tabindex': '-1', 'class': 'hp-field'}),
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'email', 'message', 'property']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone / WhatsApp'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com (optional)'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us briefly what you need'}),
            'property': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = True
        self.fields['email'].required = False

    def clean_website(self):
        value = self.cleaned_data.get('website')
        if value:
            raise forms.ValidationError('Spam detected.')
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        extra_lines = []
        looking_to_label = dict(LOOKING_TO_CHOICES).get(self.cleaned_data.get('looking_to'))
        if looking_to_label:
            extra_lines.append(f'Looking to: {looking_to_label}')
        if self.cleaned_data.get('location_preference'):
            extra_lines.append(f"Location preference: {self.cleaned_data['location_preference']}")
        if self.cleaned_data.get('budget'):
            extra_lines.append(f"Budget: {self.cleaned_data['budget']}")
        if extra_lines:
            instance.message = '\n'.join(extra_lines) + '\n\n' + instance.message
        if commit:
            instance.save()
        return instance
