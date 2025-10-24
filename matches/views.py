from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import Match, MatchPlayer, Field
from .forms import CreateMatchForm
from django.db import IntegrityError
from django.core.exceptions import ValidationError # Import ValidationError
from django.http import JsonResponse # Import JsonResponse
import datetime # Import datetime

@login_required
def match_list_view(request):
    """Displays a list of pending matches that are not full and not in the past."""
    now = timezone.now()
    # Filter for matches that are pending, not full, and haven't ended yet
    available_matches = Match.objects.filter(
        status='Pending',
        match_date__gte=now.date() # Match date is today or in the future
    ).exclude(
       match_date=now.date(), end_time__lte=now.time() # Exclude if today and already ended
    ).order_by('match_date', 'start_time')

    # Further filter out full matches (can't directly filter on property in Django < 4)
    matches_to_display = [match for match in available_matches if not match.is_full]

    context = {
        'matches': matches_to_display,
        'match_count': len(matches_to_display)
    }
    return render(request, 'match_list.html', context)

@login_required
def create_match_view(request):
    """Handles the creation of a new match."""
    if request.method == 'POST':
        form = CreateMatchForm(request.POST)
        if form.is_valid():
            try:
                match = form.save(commit=False)
                match.organizer = request.user
                
                # --- UPDATE: Get start/end time from cleaned_data ---
                match.start_time = form.cleaned_data['start_time']
                match.end_time = form.cleaned_data['end_time']
                
                # Sport is set automatically in model's save method
                # The form's clean method already checked for conflicts
                match.save() 

                # Automatically add the organizer as the first player
                MatchPlayer.objects.create(match=match, user=request.user)

                messages.success(request, f"Match room created successfully for {match.field.name} on {match.match_date}.")
                return redirect('matches:match_list') # Redirect to the match list
                
            except ValidationError as e:
                # This might be redundant if form.clean() catches everything
                messages.error(request, f"Failed to create match: {e.messages[0]}")
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {e}")
        else:
            # Form validation failed
            messages.error(request, "Please correct the errors below.")
    else: # GET request
        form = CreateMatchForm(initial={'match_date': timezone.now().date()}) # Set initial date

    context = {'form': form}
    return render(request, 'create_match_form.html', context)

@login_required
@require_POST # Ensure only POST requests can join
def join_match_view(request, match_id):
    """Handles a user joining a match."""
    match = get_object_or_404(Match, pk=match_id)

    # Prevent joining if not pending, past, or full
    if match.status != 'Pending':
        messages.error(request, "This match is no longer available to join.")
        return redirect('matches:match_list')
    if match.is_past_match:
         messages.error(request, "This match has already passed.")
         return redirect('matches:match_list')
    if match.is_full:
        messages.error(request, "This match is already full.")
        return redirect('matches:match_list')

    # Try to add the player
    try:
        MatchPlayer.objects.create(match=match, user=request.user)
        messages.success(request, f"Successfully joined the match at {match.field.name}.")
        # Check if the match is now full after joining
        if match.is_full:
             # Optionally update status to Confirmed if full means confirmed
             # match.status = 'Confirmed'
             # match.save()
             messages.info(request, "The match is now full!")
    except IntegrityError:
        # This happens if the user is already in the match (due to unique_together)
        messages.warning(request, "You have already joined this match.")
    except Exception as e:
         messages.error(request, f"An error occurred while joining: {e}")


    return redirect('matches:match_list') # Redirect back to the list


# --- NEW VIEW ---
@login_required
def get_match_slots_ajax(request):
    """
    AJAX view to get the status of all match slots for a given field and date.
    Checks against both Bookings and other Matches.
    """
    field_id = request.GET.get('field_id')
    date_str = request.GET.get('date')

    if not field_id or not date_str:
        return JsonResponse({'error': 'Field ID and Date parameters are required'}, status=400)

    try:
        booking_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        today = timezone.now().date()
        # You might want a max_date check here too, similar to bookings
        if booking_date < today:
             return JsonResponse({'slots': [], 'message': 'Cannot check availability for past dates.'})
    
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
    except TypeError:
        return JsonResponse({'error': 'Invalid date or field.'}, status=400)
    
    try:
        field_id_int = int(field_id)
        if not Field.objects.filter(pk=field_id_int).exists():
             return JsonResponse({'error': 'Field not found.'}, status=404)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid Field ID.'}, status=400)


    # Get slots using the model's static method
    all_slots = Match.get_all_slots_status(field_id_int, booking_date)
    
    return JsonResponse({'slots': all_slots})

