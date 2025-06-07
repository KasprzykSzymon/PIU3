from django.db import migrations

def set_default_reservation_price(apps, schema_editor):
    Reservation = apps.get_model('polls', 'Reservation')
    Reservation.objects.filter(reservation_price__isnull=True).update(reservation_price=7000)
    Reservation.objects.filter(reservation_price='').update(reservation_price=7000)

class Migration(migrations.Migration):
    dependencies = [
        ('polls', '0002_alter_reservation_reservation_price'),
    ]
    operations = [
        migrations.RunPython(set_default_reservation_price),
    ]