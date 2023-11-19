import json
import os
from django.shortcuts import get_object_or_404, render
from .models import UserPreference
from django.conf import settings
from  django.contrib import messages


# Create your views here.
def userpreference(request):
    currency_list  = []

    file_path = os.path.join(settings.BASE_DIR ,'currencies.json')
    with open(file_path,'r') as json_file:
        data = json.load(json_file)

        for  k,v in data.items():
            currency_list.append({'name':k,'value':v})
    
    user_preferences = UserPreference.objects.filter(user=request.user).first()

    if request.method == 'POST':
        currency = request.POST.get('currency')

        if user_preferences:
            user_preferences.currency = currency
            messages.success(request, "Changes Updated")
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
            messages.success(request, 'Changes saved')

    context = {'currency_list': currency_list, 'user_preferences': user_preferences}
    return render(request, 'userpreference/index.html', context)






    