import datetime 
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Reservation, Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from logic.register import majority
from django.contrib.auth.models import User
from .forms import UserProfileForm
from .payment_helpers import new_payment, check_payment
import uuid
import json
from django.utils import timezone

def home_page_view(request):
    return render(request, 'home_page.html')


def reservation_view(request):
    arrival_date = request.GET.get('arrival_date')
    adults = int(request.GET.get('adults', 1))

    # aktualny czas + 1,5h
    now = timezone.localtime()
    limit_datetime = now + datetime.timedelta(hours=1, minutes=30)

    # Dostępne godziny
    times = []
    start_time = datetime.datetime.strptime("10:00", "%H:%M")
    end_time = datetime.datetime.strptime("18:00", "%H:%M")
    current_time = start_time

    while current_time <= end_time:
        # Jeśli to dziś, filtruj niedozwolone godziny
        if arrival_date == now.date().isoformat():
            current_full = datetime.datetime.combine(now.date(), current_time.time())
            if current_full < limit_datetime:
                current_time += datetime.timedelta(minutes=60)
                continue
        times.append(current_time.strftime("%H:%M"))
        current_time += datetime.timedelta(minutes=60)

    context = {
        'range_10x': range(6, 21),
        'arrival_date': arrival_date,
        'adults': adults,
        'available_times': times,
        'min_date': (now + datetime.timedelta(hours=1.5)).date().isoformat(),
        'today': now.date().isoformat(),
    }
    return render(request, 'reservation.html', context)

@login_required(login_url='sign_in')
def reserve_action(request):
    if request.method == 'POST':
        num_people = request.POST['num_people']
        reservation_date = request.POST['reservation_date']
        reservation_time = request.POST['reservation_time']
        reservation_price = Reservation.reservation_price
    payment = Payment()
    payment.amount = reservation_price
    payment.save()

    reservation = Reservation()
    reservation.user = request.user
    reservation.reservation_date = reservation_date
    reservation.reservation_time = reservation_time
    reservation.num_people = num_people
    reservation.payment_status = payment
    reservation.save()

    myuuid = uuid.uuid4()
    if not payment.paynow_id:
        paynow = new_payment({
            "amount": reservation_price,
            "description": 'Opłata za reserwacje',
            "externalId": str(payment.id),
            "buyer": {
                "email": request.user.email,
                "phone": {
                    "prefix": "+48",
                    "number": "112112112"
                }
            },
            "continueUrl": f"http://127.0.0.1:8000/payment_confirmation?reservation={str(reservation.id)}"
        }, str(myuuid))
        payment.last_response = json.dumps(paynow)
        payment.status = paynow['status']
        payment.paynow_id = paynow['paymentId']
        payment.redirect_url = paynow['redirectUrl']
        payment.last_update = datetime.datetime.now()
        payment.save()
    return HttpResponseRedirect(paynow['redirectUrl'])

@login_required(login_url='sign_in')
def order_confirmation(request):
    reservation_id = int(request.GET['reservation'])
    reservation = Reservation.objects.get(id=reservation_id)
    payment = reservation.payment_status

    # Sprawdzenie aktualnego statusu płatności w PayNow
    check = check_payment(payment.paynow_id)
    current_status = check.get('status', 'UNKNOWN')

    # Zapisz aktualny status do obiektu
    payment.status = current_status
    payment.last_update = timezone.now()
    payment.save()

    print("Aktualny status płatności:", current_status)

    # ✅ Jeśli już opłacona — nie robimy NIC więcej
    if current_status == "CONFIRMED":
        context = {
            "adults": reservation.num_people,
            "arrival_date": reservation.reservation_date,
            "reservation_time": reservation.reservation_time
        }
        return render(request, 'reservation_successful.html', context)

    # 🔁 Tylko jeśli porzucona — PONAWIAMY
    elif current_status == "ABANDONED" and not payment.status == "CONFIRMED":
        import uuid, json
        from .payment_helpers import new_payment

        myuuid = uuid.uuid4()
        paynow = new_payment({
            "amount": payment.amount,
            "description": 'Ponowna płatność za rezerwację',
            "externalId": str(payment.id),
            "buyer": {
                "email": reservation.user.email,
                "phone": {
                    "prefix": "+48",
                    "number": "112112112"
                }
            },
            "continueUrl": f"http://127.0.0.1:8000/payment_confirmation?reservation={reservation.id}"
        }, str(myuuid))

        # 🔄 Nadpisujemy dane płatności
        payment.last_response = json.dumps(paynow)
        payment.status = paynow.get('status', 'NEW')
        payment.paynow_id = paynow.get('paymentId')
        payment.redirect_url = paynow.get('redirectUrl')
        payment.last_update = timezone.now()
        payment.save()

        return HttpResponseRedirect(payment.redirect_url)

    # ❌ Każdy inny status: redirect do anulowania
    return render(request, "payment_cancel.html")

# @login_required(login_url='sign_in')
# def retry_payment(request):
#     reservation_id = request.GET.get('reservation')
#     reservation = Reservation.objects.get(id=reservation_id)

#     # Nowa płatność
#     payment = Payment()
#     payment.amount = Reservation.reservation_price
#     payment.save()

#     reservation.payment_status = payment
#     reservation.save()

#     # Nowa płatność do Paynow
#     myuuid = uuid.uuid4()
#     paynow = new_payment({
#         "amount": payment.amount,
#         "description": 'Opłata za rezerwacje',
#         "externalId": str(payment.id),
#         "buyer": {
#             "email": request.user.email,
#             "phone": {
#                 "prefix": "+48",
#                 "number": "112112112"
#             }
#         },
#         "continueUrl": f"http://127.0.0.1:8000/payment_confirmation?reservation={reservation.id}"
#     }, str(myuuid))

#     payment.last_response = json.dumps(paynow)
#     payment.status = paynow['status']
#     payment.paynow_id = paynow['paymentId']
#     payment.redirect_url = paynow['redirectUrl']
#     payment.last_update = datetime.datetime.now()
#     payment.save()

#     return HttpResponseRedirect(paynow['redirectUrl'])      

def contact_view(request):
    return render(request, 'contact.html')

def price_list_view(request):
    return render(request, 'price_list.html')


def sign_in_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Jesteś już zalogowany.')
        return redirect('home_page')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Witaj, {user.username}! Pomyślnie zalogowano.')
            return redirect('home_page')
        else:
            messages.error(request, 'Błędny login lub hasło.')
    return render(request, 'sign_in.html')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        birthdate = request.POST.get('birthdate')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        if password != confirm_password:
            messages.error(request, 'Hasła nie są identyczne.')
            return render(request, 'register.html')
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Użytkownik o podanym adresie email już istnieje.')
            return render(request, 'register.html')
        if majority(birthdate):
            messages.error(request, 'Użytkownik nie jest pełnoletni')
            return render(request, 'register.html')
        try:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=firstname, last_name=lastname)
            user.save()
            messages.success(request, 'Rejestracja zakończona sukcesem. Zostałeś zarejestrowany.')
            return redirect('sign_in')

        except Exception as e:
            messages.error(request, f'Błąd rejestracji: {e}')
    return render(request, 'register.html')

@login_required(login_url='sign_in')
def profile_view(request):
    return render(request, 'profile.html')

@login_required(login_url='sign_in')
def edit_profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('your_data')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form': form})

@login_required(login_url='sign_in')
def your_data_view(request):
    return render(request, 'your_data.html')

@login_required(login_url='sign_in')
def your_reservations_view(request):
    now = timezone.now()

    if request.user.is_staff or request.user.is_superuser:
        reservations_qs = Reservation.objects.filter(
            reservation_date__gt=now.date()
        )
    else:
        reservations_qs = Reservation.objects.filter(
            user=request.user, reservation_date__gt=now.date()
        ).order_by('reservation_date', 'reservation_time')

    

    all_reservations = Reservation.objects.all()
    reservations_with_distance = []
    for reservation in all_reservations:
        reservation_datetime = timezone.make_aware(
            datetime.datetime.combine(reservation.reservation_date, reservation.reservation_time)
        )
        time_diff = abs((reservation_datetime - now).total_seconds())
        reservations_with_distance.append((reservation, time_diff))

    reservations_with_distance.sort(key=lambda x: x[1])
    closest_reservations = [r[0] for r in reservations_with_distance]

    context = {
        'future_reservations': reservations_qs,
        'closest_reservations': closest_reservations,
        'is_admin': request.user.is_staff or request.user.is_superuser,
        
    }
    return render(request, 'your_reservations.html', context)

@login_required(login_url='sign_in')
def history_reservations_view(request):
    now = timezone.now()

    if request.user.is_staff or request.user.is_superuser:
        reservations_qs = Reservation.objects.all()
    else:
        reservations_qs = Reservation.objects.filter(user=request.user)

    reservations_qs = reservations_qs.filter(
        reservation_date__lte=now.date()
    )

    reservations_with_distance = []
    for reservation in reservations_qs:
        reservation_datetime = timezone.make_aware(
            datetime.datetime.combine(reservation.reservation_date, reservation.reservation_time)
        )
        time_diff = abs((reservation_datetime - now).total_seconds())
        reservations_with_distance.append((reservation, time_diff))

    reservations_with_distance.sort(key=lambda x: x[1])
    closest_reservations = [r[0] for r in reservations_with_distance]

    context = {
        'closest_reservations': closest_reservations,
        'is_admin': request.user.is_staff or request.user.is_superuser,
    }

    return render(request, 'history_reservations.html', context)

def logout_view(request):
    request.session.flush()
    logout(request)
    messages.success(request, "Pomyślnie wylogowano.")
    return redirect('sign_in')