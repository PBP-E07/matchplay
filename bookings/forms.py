from django import forms
from django.utils import timezone
import datetime

# bookable times
SLOT_CHOICES = (
    ("10:00-11:00", "10:00-11:00"),
    ("11:00-12:00", "11:00-12:00"),
    ("12:00-13:00", "12:00-13:00"),
    ("13:00-14:00", "13:00-14:00"),
)

class BookingForm(forms.Form):
    # fields for the form
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring focus:ring-green-200 focus:ring-opacity-50",
            "id": "id_booking_date",
            "min": timezone.now().date().strftime("%Y-%m-%d"),
            "max": (timezone.now().date() + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
        }),
        label="Select Date",
        initial=timezone.now().date
    )

    time_slot = forms.ChoiceField(
        choices=SLOT_CHOICES,
        widget=forms.RadioSelect,
        label="Select Available Time Slot",
        required=True
    )
