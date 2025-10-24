# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from fields.models import Field
from .models import Booking
from .forms import BookingForm
from django.contrib import messages
import datetime
from django.utils import timezone

def book_field(request, field_id):
    field = get_object_or_404(Field, pk=field_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, field=field)
        if form.is_valid():
            booking_date = form.cleaned_data['booking_date']
            time_slot_str = form.cleaned_data['time_slot']
            start_time_str, end_time_str = time_slot_str.split('-')
            start_time = datetime.datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.datetime.strptime(end_time_str, '%H:%M').time()

            # Double-check availability just before saving
            if Booking.objects.filter(field=field, booking_date=booking_date, start_time=start_time).exists():
                 messages.error(request, "Sorry, this time slot was booked while you were completing the form. Please choose another slot.")
            else:
                Booking.objects.create(
                    user=request.user,
                    field=field,
                    booking_date=booking_date,
                    start_time=start_time,
                    end_time=end_time
                )
                messages.success(request, f"Successfully booked {field.name} on {booking_date} from {start_time_str} to {end_time_str}.")
                # Redirect to a success page or the user's bookings page
                return redirect('main:show_main') # Example redirect, change as needed
    else:
        # GET request: Initialize with today's date if no date is in GET params
        initial_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        form = BookingForm(field=field, initial={'booking_date': initial_date})


    # Get booked slots for the initial date to show in the calendar/UI (optional, but helpful)
    booked_slots_today = Booking.objects.filter(
        field=field,
        booking_date=initial_date
    ).values_list('start_time', flat=True)

    context = {
        'field': field,
        'form': form,
        'booked_slots': [t.strftime('%H:%M') for t in booked_slots_today] # Pass booked slots for UI indication
    }
    return render(request, 'book_field.html', context)

def get_available_slots_ajax(request, field_id):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)

    try:
        booking_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        # Basic validation: prevent checking past dates or too far in the future via AJAX
        today = timezone.now().date()
        if booking_date < today:
             return JsonResponse({'slots': [], 'message': 'Cannot check availability for past dates.'})
        if booking_date > today + datetime.timedelta(days=30):
             return JsonResponse({'slots': [], 'message': 'Can only check availability up to one month in advance.'})

    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    available_slots = Booking.get_available_slots(field_id, booking_date)
    return JsonResponse({'slots': available_slots})