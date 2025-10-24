# bookings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from fields.models import Field
from .models import Booking
from .forms import BookingForm
from django.contrib import messages
import datetime
from django.utils import timezone

@login_required
def book_field(request, field_id):
    field = get_object_or_404(Field, pk=field_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, field=field)
        if form.is_valid():
            booking_date = form.cleaned_data['booking_date']
            time_slot_str = form.cleaned_data['time_slot']

            try:
                start_time_str, end_time_str = time_slot_str.split('-')
                start_time = timezone.datetime.strptime(start_time_str, '%H:%M').time()
                end_time = timezone.datetime.strptime(end_time_str, '%H:%M').time()

                Booking.objects.create(
                    user=request.user,
                    field=field,
                    booking_date=booking_date,
                    start_time=start_time,
                    end_time=end_time
                )
                messages.success(request, f"Successfully booked {field.name} on {booking_date.strftime('%d %b %Y')} from {start_time_str} to {end_time_str}.")
                
                # --- CHANGE HERE: Redirect to "My Bookings" page ---
                return redirect('bookings:my_bookings_list')

            except ValueError:
                 messages.error(request, "Invalid time slot format received.")
    
    else:
        # GET request
        initial_date_str = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        try:
            valid_initial_date = timezone.datetime.strptime(initial_date_str, '%Y-%m-%d').date()
            today = timezone.now().date()
            max_date = today + datetime.timedelta(days=30)
            if not (today <= valid_initial_date <= max_date):
                 valid_initial_date = today
            initial_data = {'booking_date': valid_initial_date.strftime('%Y-%m-%d')}
        except ValueError:
            initial_data = {'booking_date': timezone.now().date().strftime('%Y-%m-%d')}

        form = BookingForm(field=field, initial=initial_data)

    context = {
        'field': field,
        'form': form,
    }
    return render(request, 'book_field.html', context)

def get_available_slots_ajax(request, field_id):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)

    try:
        booking_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
        today = timezone.now().date()
        max_date = today + datetime.timedelta(days=30)

        if booking_date < today:
             return JsonResponse({'slots': [], 'message': 'Cannot check availability for past dates.'})
        if booking_date > max_date:
             return JsonResponse({'slots': [], 'message': 'Can only check availability up to one month in advance.'})

    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    if not Field.objects.filter(pk=field_id).exists():
        return JsonResponse({'error': 'Field not found.'}, status=404)

    # --- CHANGE HERE: Call new method to get all slots with status ---
    all_slots = Booking.get_all_slots_status(field_id, booking_date)
    
    return JsonResponse({'slots': all_slots})


# --- NEW VIEW ---
@login_required
def my_bookings_list(request):
    """
    Shows a list of all bookings for the currently logged-in user.
    """
    # Order by upcoming bookings first, then past bookings
    bookings = Booking.objects.filter(user=request.user).order_by('booking_date', 'start_time')
    
    # Split bookings into upcoming and past
    today = timezone.now().date()
    upcoming_bookings = []
    past_bookings = []

    for booking in bookings:
        if not booking.is_past_booking:
            upcoming_bookings.append(booking)
        else:
            past_bookings.append(booking)
            
    context = {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings
    }
    return render(request, 'my_bookings.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    Shows the detail for a single booking.
    Ensures the booking belongs to the logged-in user.
    """
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    
    context = {
        'booking': booking
    }
    return render(request, 'booking_detail.html', context)