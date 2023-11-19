import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from .models import *
from userpreference.models import *
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q ,Sum
import datetime
from weasyprint import HTML

import xlwt
from reportlab.pdfgen import canvas

# Create your views here.


def home(request):
    user=request.user
    return render(request,'home.html',{'user':user})

def index(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    user = request.user if request.user.is_authenticated else None

    catagory = Category.objects.all()
    expenses = Expense.objects.filter(Q(amount__icontains=q) | Q(category__name__icontains=q) | Q(date__icontains=q) , owner=user).order_by('-date')
    paginator = Paginator(expenses ,3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency

    context={'catagories':catagory,'page_obj':page_obj,'currency':currency}
    return render(request, 'expenses/index.html',context)



def add_expenses(request):
    categories = Category.objects.all()
    if request.method == "POST":
        print(request.POST)
        amount = request.POST['amount']
        date = request.POST['expense_date']
        description = request.POST['description']
        category_name = request.POST.get('category')
        if not amount:
            messages.error(request,'Please enter the expense amount!')
            context={'fieldValues':request.POST,'categories':categories}
            return render(request, 'expenses/add-expenses.html',context)

        if not description:
            messages.error(request,'Please enter a description for this expense!')
            context={'fieldValues':request.POST,'categories':categories}
            return render(request, 'expenses/add-expenses.html',context)
        
        
        if not category_name:
            messages.error(request,'Please enter a category for this expense!')
            context={'fieldValues':request.POST,'categories':categories}
            return render(request, 'expenses/add-expenses.html',context)
        
        category = Category.objects.get(name=category_name)
        
        expense = Expense(amount=amount, category=category,owner=request.user, date=date, description=description)
        expense.save()
        messages.success(request,'Expenses saved successfully')
        return redirect('expenses')
    
    context={'categories':categories,'fieldValues':request.POST}
    return render(request, 'expenses/add-expenses.html',context)



def edit_expenses(request, pk):
    page='edit-expenses'
    categories = Category.objects.all()
    expenses = Expense.objects.get(id=pk)
    context={
        'categories':categories,
        'fieldValues':expenses,
        'page':page
    }
    if request.method == "GET":
        return render(request,'expenses/add-expenses.html',context)
    
    if request.method == "POST":
        print(request.POST)
        amount = request.POST['amount']
        category_name=request.POST.get('category')
        date = request.POST['expense_date']
        description = request.POST['description']

        if not amount:
            messages.error(request,'Please enter the expense amount!')
            context={'fieldValues':request.POST,'categories':categories}
            return render(request, 'expenses/add-expenses.html',context)

        if not description:
            messages.error(request,'Please enter a description for this expense!')
            context={'fieldValues':request.POST,'categories':categories}
            return render(request, 'expenses/add-expenses.html',context)
        
        
        if not category_name:
            messages.error(request,'Please enter a category for this expense!')
            context={'fieldValues':request.POST,'categories':categories}
            return render(request, 'expenses/add-expenses.html',context)

        expenses.amount=amount
        expenses.category=Category.objects.get(name=category_name)
        expenses.description=description
        expenses.date=date
        expenses.save()
        messages.success(request,'Expenses updated successfully')
        return redirect('expenses')
    
    return render(request,'expenses/add-expenses.html',context)

def delete_expenses(request, pk):
    expenses = Expense.objects.get(id=pk)
    expenses.delete()
    messages.info(request,"Expenses deleted")
    return redirect("expenses")


def expenses_summary(request):
    today_date = datetime.date.today()
    six_month_date = today_date - datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_month_date, date__lte=today_date)

    finalrep = {}
    print("Number of expenses:", expenses.count())

    def expenses_summary_amount(category_name):
        amount = 0
        filtered_by_category = expenses.filter(category__name=category_name)
        for item in filtered_by_category:
            amount += float(item.amount)
        return {'amount': round(amount, 2), 'name': category_name}

    for category_name in set(expenses.values_list('category__name', flat=True)):
        finalrep[category_name] = expenses_summary_amount(category_name)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)

def set_chart(request):
    # get all the categories from database and their respective amounts spent on them
    return render(request,'expenses/setchart.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    filename = "expenses_{}.csv".format(datetime.datetime.now().strftime("%Y%m%d"))
    response['Content-Disposition'] = f"attachment;filename={filename}"

    csv_writer = csv.writer(response)

    fields = ['Amount','Description','Category','Date']
    csv_writer.writerow(fields)
    expenses = Expense.objects.filter(owner= request.user)

    for row in expenses:
        csv_writer.writerow([row.amount,row.description,row.category.name,row.date])

    return response


def export_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    filename = "expenses_{}.xls".format(datetime.datetime.now().strftime("%Y%m%d"))
    response['Content-Disposition'] = f"attachment;filename={filename}"

    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('Sheet1')

    headers = ['Amount','Description','Category','Date']
    for col_num, header in enumerate(headers):
        sheet.write(0 ,col_num, header)

    data = Expense.objects.filter(owner=request.user).values_list('amount','description','category__name','date')

    for row_num, row_data in enumerate(data, start=1):
        for col_num, cell_value in enumerate(row_data):
            if isinstance(cell_value, datetime.date):
                cell_value = cell_value.strftime("%Y-%m-%d")
            sheet.write(row_num, col_num, cell_value)
    
    workbook.save(response)
    return response


def export_pdf(request):
    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum('amount'))
    # Assuming you have an HTML template named 'pdf_template.html'
    html_string = render_to_string('expenses/pdf_template.html', {'context_variable': 'Hello, PDF!', 'expenses':expenses,'total':sum['amount__sum']})
    html = HTML(string=html_string)
    
    # Generate PDF
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="output.pdf"'

    return response


