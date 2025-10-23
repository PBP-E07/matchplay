from django import forms
from fields.models import Field

class FieldForm(forms.ModelForm):
    class Meta:
        model = Field
        fields = ['name', 'sport', 'price', 'rating', 'location', 'facilities', 'image', 'url']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded px-2 py-1 w-full'}),
            'sport': forms.Select(attrs={'class': 'border rounded px-2 py-1 w-full'}),
            'price': forms.NumberInput(attrs={'class': 'border rounded px-2 py-1 w-full'}),
            'rating': forms.NumberInput(attrs={'class': 'border rounded px-2 py-1 w-full'}),
            'location': forms.TextInput(attrs={'class': 'border rounded px-2 py-1 w-full'}),
            'facilities': forms.CheckboxSelectMultiple(),
            'image': forms.TextInput(attrs={'class': 'border rounded px-2 py-1 w-full'}),
            'url': forms.TextInput(attrs={'class': 'border rounded px-2 py-1 w-full'}),
        }
