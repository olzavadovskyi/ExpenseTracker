from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.register_view, name='register'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('expense-detail/', views.expense_detail, name='expense_detail'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('manage-categories/', views.manage_categories, name='manage_categories'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),
    path('sign-in/', views.sign_in_view, name='sign_in'),
    path('statistics/', views.statistics, name='statistics'),
    path('logout/', views.logout_view, name='logout'),
]
