from django.contrib import admin
from .models import *
# Register your models here.
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('amount','description','owner','category','date')
    search_fields = ('amount','description','category__name')


admin.site.register(Expense, ExpensesAdmin)
admin.site.register(Category)
