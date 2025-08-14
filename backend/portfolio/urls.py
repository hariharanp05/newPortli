from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_portfolio, name='create-portfolio'),
    path('user/', views.get_portfolio_by_user, name='get-user-portfolio'),
    path('<str:portfolio_id>/edit/', views.update_portfolio, name='edit-portfolio'),
    path('<str:portfolio_id>/delete/', views.delete_portfolio, name='delete-portfolio'),
    path('public/<str:username>/', views.get_public_portfolio, name='get_public_portfolio'),
]
