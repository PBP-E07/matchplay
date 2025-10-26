from django.urls import path
from bookings.views import get_slots_ajax, show_book, show_booking_detail, show_my_bookings

app_name = "bookings"

urlpatterns = [
    path("book/<int:field_id>/", show_book, name="show_book"),
    path("get_slots/<int:field_id>/", get_slots_ajax, name="get_slots_ajax"),
    path("my_bookings/", show_my_bookings, name="show_my_bookings"),
    path("detail/<int:booking_id>/", show_booking_detail, name="show_booking_detail"),
]
