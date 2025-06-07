from django.contrib import admin
from .models import Reservation, Payment

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reservation_date', 'reservation_time', 'num_people', 'payment_status')
    list_filter = ('reservation_date', 'payment_status')
    search_fields = ('user__username', 'id')

# @admin.register(Payment)
# class Payment(admin.ModelAdmin):
#     pass

@admin.register(Payment)
class Payment(admin.ModelAdmin):
    pass


