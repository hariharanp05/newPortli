from django.urls import path
from . import views

urlpatterns = [
    path('save/', views.save_portfolio, name='save-portfolio'),
    path('user/', views.get_portfolio_by_user, name='get-user-portfolio'),
    path('<str:user_id>/delete/', views.delete_portfolio, name='delete-portfolio'),
    path('public/<str:username>/', views.get_public_portfolio, name='get_public_portfolio'),
]
