from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('',views.index,name="income"),
    path('add-income',views.add_income,name="add-income"),
    path('edit-income/<str:pk>/',views.edit_income,name="edit-income"),
    path('delete-income/<str:pk>/',views.delete_income,name="delete-income"),
    path('search-income/',csrf_exempt(views.search_income),name="search-income"),
    path('income-summary/',csrf_exempt(views.income_summary),name="income-summary"),
    path('income-stats/',csrf_exempt(views.income_stats),name="income-stats"),
]
