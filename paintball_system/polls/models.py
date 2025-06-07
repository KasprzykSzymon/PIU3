#models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

class Payment(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.TextField(null=True)
    amount = models.IntegerField()
    paynow_id = models.TextField(null=True)
    redirect_url = models.TextField(null=True)
    request = models.TextField(null=True)
    last_response = models.TextField(null=True)
    last_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.status or 'Brak statusu'} - {self.amount / 100:.2f} PLN"

class Reservation(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    num_people = models.IntegerField()
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    reservation_price = 7000
    payment_status = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, null=True, blank=True)
    

    def __str__(self):
        return f"Rezerwacja Zaakceptowana"

    def is_future_reservation(self):
        reservation_datetime = timezone.make_aware(
            datetime.datetime.combine(self.reservation_date, self.reservation_time)
        )
        return reservation_datetime >= timezone.now()

    def is_past_reservation(self):
        return not self.is_future_reservation()