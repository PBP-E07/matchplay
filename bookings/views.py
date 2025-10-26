from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from fields.models import Field
from matches.models import Match
from .models import Booking
from .forms import BookingForm
from django.contrib import messages
import datetime
from django.utils import timezone

def get_slots_ajax(request, field_id):
    # get the date from the sent form
    date = request.GET.get("date")

    # make it comparable
    booking_date = timezone.datetime.strptime(date, "%Y-%m-%d").date()

    # get today's date
    today = timezone.now().date()

    # maximum booking time is one month after today
    max_date = today + datetime.timedelta(days=30)

    if booking_date > max_date:
        return JsonResponse({ "error": "Cannot check availability more than 30 days in advance.", "slots": [] }, status=400)

    Field.objects.get(pk=field_id)

    # get booked times (unavailable times)
    booked_times = set(
        Booking.objects.filter(field_id=field_id, booking_date=booking_date).values_list("start_time", flat=True)
    )

    match_times = set(
        Match.objects.filter(
            field_id=field_id, 
            match_date=booking_date, 
            status__in=["Pending", "Confirmed"]
        ).values_list("start_time", flat=True)
    )
    
    unavailable_times = booked_times.union(match_times)

    slots = [
        (datetime.time(10, 0), datetime.time(11, 0)),
        (datetime.time(11, 0), datetime.time(12, 0)),
        (datetime.time(12, 0), datetime.time(13, 0)),
        (datetime.time(13, 0), datetime.time(14, 0)),
    ]

    slots_with_status = []
    
    now_time = timezone.localtime(timezone.now()).time()

    for start, end in slots:
        is_unavailable = start in unavailable_times

        is_booked = start in booked_times

        is_past = (booking_date < today) or (booking_date == today and start < now_time)

        # assign status based on slot availability
        status = "available"

        if is_past:
            status = "past"
        elif is_unavailable:
            if start in booked_times:
                status = "booked"
            else:
                status = "match_created"

        slots_with_status.append({
            "start": start.strftime("%H:%M"),
            "end": end.strftime("%H:%M"),
            "status": status
        })

    return JsonResponse({ "slots": slots_with_status })

@login_required
def show_book(request, field_id):
    field = get_object_or_404(Field, pk=field_id)

    if request.method == "POST":
        form = BookingForm(request.POST)

        if form.is_valid():
            booking_date = form.cleaned_data["booking_date"]
            time_slot_str = form.cleaned_data["time_slot"]

            start_time_str, end_time_str = time_slot_str.split("-")
            start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
            end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()

            now = timezone.localtime(timezone.now())

            # validate times
            if start_time and booking_date == now.date() and start_time < now.time():
                messages.error(request, "Cannot book a time slot that has already passed today.")

            is_already_booked = False

            if start_time and not is_already_booked:
                is_already_booked = Booking.objects.filter(
                    field=field,
                    booking_date=booking_date,
                    start_time=start_time
                ).exists()

                # error message if slot is already booked
                if is_already_booked:
                    messages.error(request, "Sorry, this time slot was just booked. Please select another.")

            if not is_already_booked and start_time and end_time:
                Booking.objects.create(
                    user=request.user,
                    field=field,
                    booking_date=booking_date,
                    start_time=start_time,
                    end_time=end_time
                )
                messages.success(request, "Successfully booked")

                return redirect("bookings:show_my_bookings")
                
            else:
                messages.error(request, "Booking failed. Please correct the errors below.")
        else:
            messages.error(request, "Booking failed. Please correct the errors below.")

    else:
        initial_date_str = request.GET.get("date", timezone.now().date().strftime("%Y-%m-%d"))
        initial_data = { "booking_date": initial_date_str }
        form = BookingForm(initial=initial_data)

    context = {
        "field": field,
        "form": form,
    }

    return render(request, "book.html", context)

@login_required
def show_my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('field').order_by("-booking_date", "-start_time")
    
    upcoming_bookings = []
    past_bookings = []

    now = timezone.now()
    for booking in bookings:
        combined_end_dt = datetime.datetime.combine(booking.booking_date, booking.end_time)
        booking_end_dt = timezone.make_aware(combined_end_dt) if timezone.is_naive(combined_end_dt) else combined_end_dt
        is_past = booking_end_dt < now

        if is_past:
            past_bookings.append(booking)
        else:
            upcoming_bookings.append(booking)

        booking.is_past = is_past

    context = { "upcoming_bookings": upcoming_bookings, "past_bookings": past_bookings }

    return render(request, "my_bookings.html", context)

@login_required
def show_booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)

    now = timezone.now()

    combined_end_dt = datetime.datetime.combine(booking.booking_date, booking.end_time)
    booking_end_dt = timezone.make_aware(combined_end_dt) if timezone.is_naive(combined_end_dt) else combined_end_dt
    booking.is_past = booking_end_dt < now

    context = { "booking": booking }
    return render(request, "booking_detail.html", context)
