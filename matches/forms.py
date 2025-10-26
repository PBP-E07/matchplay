from django import forms
from .models import Match, Field, Booking
from django.utils import timezone
import datetime

class CreateMatchForm(forms.ModelForm):
    # Use DateInput and TimeInput for better browser support
    match_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
        label="Date"
    )

    # --- ADDED time_slot field ---
    time_slot = forms.ChoiceField(
        choices=[], # Dynamically populated
        widget=forms.RadioSelect,
        label="Select Time Slot",
        required=True
    )

    class Meta:
        model = Match
        # --- UPDATED fields list ---
        fields = [
            'field', 'match_date', 'time_slot',
            'skill_level', 'max_players', 'price_per_person', 'description'
        ]
        widgets = {
            'field': forms.Select(attrs={'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'id': 'id_field'}), # Add ID
            'skill_level': forms.Select(attrs={'class': 'form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50'}),
            'max_players': forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'min': '2'}),
            'price_per_person': forms.NumberInput(attrs={'class': 'form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50', 'rows': 3}),
        }
        labels = {
            'price_per_person': 'Price per Person (Rp)',
            'max_players': 'Max Players (including you)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set min date for date picker
        today = timezone.now().date()
        self.fields['match_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        # Add ID for JS targeting
        self.fields['match_date'].widget.attrs['id'] = 'id_match_date'

        # --- DYNAMIC TIME SLOT POPULATION (for initial load/form re-render) ---
        initial_field = self.initial.get('field') or self.data.get('field')
        initial_date_str = self.initial.get('match_date') or self.data.get('match_date')
        
        initial_date = None
        if initial_date_str:
            try:
                # Handle potential date object or string
                initial_date = datetime.datetime.strptime(str(initial_date_str), '%Y-%m-%d').date()
            except ValueError:
                initial_date = today
        else:
            initial_date = today

        if initial_field and initial_date:
            all_slots = Match.get_all_slots_status(initial_field, initial_date)
            # Populate choices so validation can work on POST
            self.fields['time_slot'].choices = [
                (f"{slot['start']}-{slot['end']}", f"{slot['start']} - {slot['end']}")
                for slot in all_slots # Template will handle disabling, form just needs choices
            ]
        else:
            # Provide empty choices if no field/date selected yet
            self.fields['time_slot'].choices = []


    def clean(self):
        """Custom validation for the form."""
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        match_date = cleaned_data.get('match_date')
        time_slot_str = cleaned_data.get('time_slot')

        start_time = None # Initialize start_time as None

        if not time_slot_str:
             # Will be caught by required=True, but good to check
             return cleaned_data
        
        try:
            start_time_str, end_time_str = time_slot_str.split('-')
            start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()
            
            # Store these on the cleaned_data dict for the view to use
            cleaned_data['start_time'] = start_time
            cleaned_data['end_time'] = end_time

        except (ValueError, TypeError):
            self.add_error('time_slot', "Invalid time slot format.")
            return cleaned_data # Return immediately on failure

        # Check if fields are missing from cleaned_data (e.g., failed basic validation)
        if not field or not match_date:
            return cleaned_data

        # 2. Check match date/time is not in the past
        now = timezone.now()
        if match_date < now.date():
            self.add_error('match_date', "Cannot create a match for a past date.")
        # Check that start_time is not None before comparing
        elif match_date == now.date() and start_time and start_time <= now.time():
            self.add_error('time_slot', "This time slot is in the past.")

        # 3. Check for booking conflicts (CRUCIAL)
        # Only run these checks if start_time was successfully parsed
        if start_time:
            is_booked = Booking.objects.filter(
                field=field,
                booking_date=match_date,
                start_time=start_time
            ).exists()
            if is_booked:
                self.add_error('time_slot', f"This time slot is already booked directly.")

            # 4. Check for match conflicts
            # --- THIS IS THE FIX ---
            # Base query
            match_conflict_qs = Match.objects.filter(
                field=field,
                match_date=match_date,
                start_time=start_time,
                status__in=['Pending', 'Confirmed']
            )
            
            # If we are *editing* an existing match, exclude it from the conflict check
            if self.instance and self.instance.pk:
                match_conflict_qs = match_conflict_qs.exclude(pk=self.instance.pk)
            
            # Now check if any *other* match exists
            if match_conflict_qs.exists():
                 self.add_error('time_slot', f"This time slot is already taken by another match.")

        return cleaned_data
