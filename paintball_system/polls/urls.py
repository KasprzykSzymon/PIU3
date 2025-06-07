from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page_view, name='home_page'),
    path('payment_confirmation/', views.order_confirmation, name='order_confirmation'),
    # path('retry_payment/', views.retry_payment, name='retry_payment'),
    path('rezerwacja/', views.reservation_view, name='reservation'),
    path('rezerwacja_akcja/', views.reserve_action, name='reserve_action'),
    path('kontakt/', views.contact_view, name='contact'),
    path('cennik/', views.price_list_view, name='price_list'),
    path('zaloguj_sie/', views.sign_in_view, name='sign_in'),
    path('rejestracja/', views.register_view, name='register'),
    path('profil/', views.profile_view, name='profile'),
    path('twoje_dane/', views.your_data_view, name='your_data'),
    path('edytuj_profil/', views.edit_profile_view, name='edit_profile'),
    path('twoje_rezerwacje/', views.your_reservations_view, name='your_reservations'),
    path('historia_rezerwacji/', views.history_reservations_view, name='history_reservations'),
    path('logout/', views.logout_view, name='logout'),
] 