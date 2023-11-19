import datetime
import json
from django.http import JsonResponse
from django.shortcuts import redirect, render
from .models import *
from django.contrib import messages
from userpreference.models import *
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

# Create your views here.

def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText').lower()
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            description__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__name__icontains=search_str, owner=request.user)
        data = income.values('amount', 'source__name', 'description', 'date')
        return JsonResponse(list(data), safe=False)


def index(request):   
    source = Source.objects.all()
    income = Income.objects.filter( owner=request.user)
    paginator = Paginator(income ,2)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency

    context={'source':source,'page_obj':page_obj,'currency':currency}
    return render(request, 'income/index.html',context)



def add_income(request):
    source = Source.objects.all()
    if request.method == "POST":
        print(request.POST)
        amount = request.POST['amount']
        date = request.POST['income_date']
        description = request.POST['description']
        source_name = request.POST.get('source')
        if not amount:
            messages.error(request,'Please enter the Income amount!')
            context={'fieldValues':request.POST,'source':source}
            return render(request, 'income/add_edit_income.html',context)

        if not description:
            messages.error(request,'Please enter a description for this Income!')
            context={'fieldValues':request.POST,'source':source}
            return render(request, 'income/add_edit_income.html',context)
        
        
        if not source_name:
            messages.error(request,'Please enter a Source for this Income!')
            context={'fieldValues':request.POST,'source':source}
            return render(request, 'income/add_edit_income.html',context)
        
        source = Source.objects.get(name=source_name)
        
        income = Income(amount=amount, source=source,owner=request.user, date=date, description=description)
        income.save()
        messages.success(request,'Incomes saved successfully')
        return redirect('income')
    
    context={'source':source,'fieldValues':request.POST}
    return render(request, 'income/add_edit_income.html',context)



def edit_income(request, pk):
    page='edit-income'
    source = Source.objects.all()
    income = Income.objects.get(id=pk)
    context={
        'source':source,
        'fieldValues':income,
        'page':page
    }
    if request.method == "GET":
        return render(request,'income/add_edit_income.html',context)
    
    if request.method == "POST":
        print(request.POST)
        amount = request.POST['amount']
        source_name=request.POST.get('source')
        date = request.POST['income_date']
        description = request.POST['description']

        if not amount:
            messages.error(request,'Please enter the Income amount!')
            context={'fieldValues':request.POST,'source':source}
            return render(request, 'income/add_edit_income.html',context)

        if not description:
            messages.error(request,'Please enter a description for this Income!')
            context={'fieldValues':request.POST,'source':source}
            return render(request, 'income/add_edit_income.html',context)
        
        
        if not source_name:
            messages.error(request,'Please enter a Source for this Income!')
            context={'fieldValues':request.POST,'source':source}
            return render(request, 'income/add_edit_income.html',context)

        income.amount=amount
        income.source=Source.objects.get(name=source_name)
        income.description=description
        income.date=date
        income.save()
        messages.success(request,'Incomes updated successfully')
        return redirect('income')
    
    return render(request,'income/add_edit_income.html',context)

def delete_income(request, pk):
    income = Income.objects.get(id=pk)
    income.delete()
    messages.info(request,"Income deleted")
    return redirect("income")


def income_summary(request):
    today_date = datetime.date.today()
    six_month_date = today_date - datetime.timedelta(days=30*6)
    incomes = Income.objects.filter(owner=request.user, date__gte=six_month_date, date__lte=today_date)

    finalrep ={}

    def income_summary_amount(source_name):
        amount = 0
        filtered_by_income = incomes.filter(source__name=source_name)
        for i in filtered_by_income:
            amount +=i.amount
        return {'amount': round(amount, 2), 'name': source_name}
    
    for source_name in incomes.values_list('source__name',flat=True):
        finalrep[source_name] = income_summary_amount(source_name)
    
    return JsonResponse({'income_summary_data':finalrep},safe=False)


def income_stats(request):
    return render(request,'income/income_stats.html')



