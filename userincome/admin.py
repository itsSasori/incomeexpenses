from django.contrib import admin
from .models import *
# Register your models here.
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('amount','description','owner','source','date')
    search_fields = ('amount','description','source__name')


admin.site.register(Income, IncomeAdmin)
admin.site.register(Source)
