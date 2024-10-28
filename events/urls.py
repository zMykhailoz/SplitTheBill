from django.urls import path
from . import views
from .views import create_event, add_expense, register


urlpatterns = [
    path('', views.home, name='home'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('create/', create_event, name='create_event'),
    path('event/<int:event_id>/add_expense/', add_expense, name='add_expense'),
    path('add_friend/<int:friend_id>/', views.add_friend, name='add_friend'),
    path('event/<int:event_id>/complete/', views.complete_event, name='complete_event'),
    path('add_debt/<int:borrower_id>/<int:amount>/', views.add_debt, name='add_debt'),
    path('profile/', views.profile, name='profile'),
    path('register/', register, name='register'),
    path('send_friend_request/<int:friend_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('remove_friend/<int:friend_id>/', views.remove_friend, name='remove_friend'),

]
