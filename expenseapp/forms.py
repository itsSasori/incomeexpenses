from django.forms import ModelForm
from .models import *

#Create your form here.

class NoteForm(ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'