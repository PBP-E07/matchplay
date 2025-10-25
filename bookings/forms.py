from django import forms
from bookings.models import Booking
import datetime
from django.utils import timezone

class BookingForm(forms.Form):
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={ "type": "date" }),
        label="Select Date"
    )

    time_slot = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        label="Select Time Slot"
    )

    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop('field', None)
        super().__init__(*args, **kwargs)

        today = timezone.now().date()
        max_date = today + datetime.timedelta(days=30)
        self.fields['booking_date'].widget.attrs.update({
            'min': today.strftime('%Y-%m-%d'),
            'max': max_date.strftime('%Y-%m-%d')
        })

        initial_date_str = self.data.get('booking_date') if self.data else None
        initial_date = None
        if initial_date_str:
            try:
                initial_date = datetime.datetime.strptime(initial_date_str, '%Y-%m-%d').date()
            except ValueError:
                initial_date = today
        else:
           initial_date = today

        if self.field and initial_date:
            available_slots = Booking.get_available_slots(self.field.id, initial_date)
            self.fields['time_slot'].choices = [
                (f"{slot['start']}-{slot['end']}", f"{slot['start']} - {slot['end']}")
                for slot in available_slots
            ]

    def clean_booking_date(self):
        date = self.cleaned_data.get('booking_date')
        if date < timezone.now().date():
            raise forms.ValidationError("You cannot book a date in the past.")
        if date > timezone.now().date() + datetime.timedelta(days=30):
             raise forms.ValidationError("You can only book up to one month in advance.")
        return date

    def clean_time_slot(self):
        time_slot_str = self.cleaned_data.get('time_slot')
        booking_date = self.cleaned_data.get('booking_date') # Use cleaned date

        if not time_slot_str or not booking_date:
            return time_slot_str

        start_time_str, end_time_str = time_slot_str.split('-')
        start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()

        if Booking.objects.filter(field=self.field, booking_date=booking_date, start_time=start_time).exists():
            raise forms.ValidationError("This time slot has just been booked. Please choose another one.")

        return time_slot_str
