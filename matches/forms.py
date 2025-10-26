from django import forms
from .models import Match, Field
from django.utils import timezone
import datetime

SLOT_CHOICES = (
    ("10:00-11:00", "10:00-11:00"),
    ("11:00-12:00", "11:00-12:00"),
    ("12:00-13:00", "12:00-13:00"),
    ("13:00-14:00", "13:00-14:00"),
)

class CreateMatchForm(forms.Form):
    field = forms.ModelChoiceField(
        queryset=Field.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 
            'id': 'id_field'
        }),
        label="Field"
    )
    
    match_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
            'id': 'id_match_date',
            'min': timezone.now().date().strftime('%Y-%m-%d'),
            'max': (timezone.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
        }),
        label="Date",
        initial=timezone.now().date
    )

    time_slot = forms.ChoiceField(
        choices=SLOT_CHOICES,
        widget=forms.RadioSelect,
        label="Select Time Slot",
        required=True
    )
    
    skill_level = forms.ChoiceField(
        choices=Match.LEVEL_CHOICES,
        initial='All Levels',
        widget=forms.Select(attrs={'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        label="Skill Level"
    )

    max_players = forms.IntegerField(
        min_value=2,
        widget=forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'min': '2'}),
        label="Max Players (including you)"
    )

    price_per_person = forms.DecimalField(
        min_value=0,
        initial=0.00,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'step': '0.01'}),
        label="Price per Person (Rp)"
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'rows': 3}),
        required=False,
        label="Description",
        help_text="Add any extra details, e.g., 'Mixed skill levels, just have fun!'"
    )