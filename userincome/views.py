from django.shortcuts import render,redirect
from .models import Source,UserIncome
from django.core.paginator import Paginator
from userpreferences.models import userpreferences
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse

# Create your views here.
@login_required(login_url='authentication/login')
def index(request):
    # Query the Expense model using the correct field
    income = UserIncome.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(income, 2)  # Paginate results
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Handle user preferences for currency
    try:
        currency = userpreferences.objects.get(user=request.user).currency
    except userpreferences.DoesNotExist:
        currency = 'Default Currency'  # Fallback if user preferences are missing

    # Pass context to the template
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'income/index.html', context)

def add_income(request):
    sources=Source.objects.all()
    context={
        'sources':sources,
        'values':request.POST
    }
    if request.method=='GET':
        return render(request,'income/add_income.html', context)


    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/add_income.html', context)
        
        UserIncome.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request,'Record saved successfully!!')
        return redirect('income')
    

@login_required(login_url='authentication/login')
def income_edit(request,id):
    sources=Source.objects.all()
    income=UserIncome.objects.get(pk=id)
    context={
        'income':income,
        'values':income,
        'sources':sources,
    }
    if request.method=='GET':
        return render(request,'income/edit-income.html',context)
    if request.method=='POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request,'Amount is required')
            return render(request,'income/edit-income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['sources']

        if not description:
            messages.error(request,'Description is required')
            return render(request,'income/edit_income.html', context)
        
        income.amount=amount 
        income.date=date
        income.source= source
        income.description=description
        income.save()
        messages.success(request,'Record Updated successfully!!')
        return redirect('income')


def delete_income(request,id):
    income=UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request,'Record removed')
    return redirect('income')   

def search_income(request):
    if request.method=='POST':
        search_str=json.loads(request.body).get('searchText')
        income=UserIncome.objects.filter(
            amount__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str,owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str,owner=request.user) | UserIncome.objects.filter(
            source__istartswith=search_str,owner=request.user)
        data=income.values()
        return JsonResponse(list(data),safe=False) 

