from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import Match, MatchPlayer
from .forms import CreateMatchForm
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# --- ADD THESE TWO IMPORTS ---
import datetime
from fields.models import Field 
# --- END ADDITIONS ---

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

    # Further filter out full matches
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
        form = CreateMatchForm(request.POST) # Bind form to POST data
        if form.is_valid():
            try:
                match = form.save(commit=False)
                match.organizer = request.user
                
                # Get start_time and end_time from the form's cleaned data
                match.start_time = form.cleaned_data['start_time']
                match.end_time = form.cleaned_data['end_time']
                
                match.save() # This calls model.clean()

                # Automatically add the organizer as the first player
                MatchPlayer.objects.create(match=match, user=request.user)

                messages.success(request, f"Match room created successfully for {match.field.name} on {match.match_date}.")
                return redirect('matches:match_list') # Redirect to the match list
            
            except ValidationError as e:
                # Catch validation errors raised from model.clean()
                # Add this as a non-field error to the *existing* form
                form.add_error(None, e.messages[0])
                messages.error(request, "Please correct the errors below.")
            except Exception as e:
                # Catch other unexpected errors
                form.add_error(None, f"An unexpected error occurred: {e}")
                messages.error(request, "An unexpected error occurred. Please try again.")
            
            # If try/except failed, we fall through to render the *same* form object
        
        else:
            # form.is_valid() was False.
            messages.error(request, "Please correct the errors below.")
        
        # --- Key Change ---
        # On a failed POST (either form.is_valid()=False or try/except failure),
        # render the *existing* 'form' object which contains the errors.
        context = {'form': form}
        return render(request, 'create_match_form.html', context)

    else: # GET request
        form = CreateMatchForm() # Create a new, empty form
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
             messages.info(request, "The match is now full!")
    except IntegrityError:
        # This happens if the user is already in the match (due to unique_together)
        messages.warning(request, "You have already joined this match.")
    except Exception as e:
         messages.error(request, f"An error occurred while joining: {e}")


    return redirect('matches:match_list') # Redirect back to the list

# AJAX view for getting slots
def get_match_slots_ajax(request, field_id):
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)
    
    try:
        booking_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    # Get slots status from model
    try:
        all_slots = Match.get_all_slots_status(field_id, booking_date)
        return JsonResponse({'slots': all_slots})
    except Field.DoesNotExist:
        return JsonResponse({'error': 'Field not found.'}, status=404)
