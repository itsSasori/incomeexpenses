from django.urls import path
from . import views
urlpatterns = [
    path('expenses/',views.index,name="expenses"),
    path('',views.home,name="index"),
    path('add-expenses/',views.add_expenses,name="add-expenses"),
    path('edit-expenses/<str:pk>/',views.edit_expenses,name="edit-expenses"),
    path('delete-expenses/<str:pk>/',views.delete_expenses,name="delete-expenses"),
    path('expense-summary',views.expenses_summary,name="expenses-summary"),
    path('set-chart/',views.set_chart,name="set-chart"),
    path('export-csv/',views.export_csv,name="export-csv"),
    path('export-xls/',views.export_xls,name="export-xls"),
    path('export-pdf/',views.export_pdf,name="export-pdf"),
]
