import pyrebase
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from time import time

config = {
  'apiKey': "AIzaSyAkDP2AhobRcAhWelrptCPc8ftXzDLSww0",
  'authDomain': "chemo-8da83.firebaseapp.com",
  'databaseURL': "https://chemo-8da83.firebaseio.com",
  'projectId': "chemo-8da83",
  'storageBucket': "chemo-8da83.appspot.com",
  'messagingSenderId': "699405303797",
  'appId': "1:699405303797:web:729d397cf843942fe22abc",
  'measurementId': "G-9R3DK327S3"
}
firebase = pyrebase.initialize_app(config)


# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    db = firebase.database()
    name = db.child("suppliers").child(request.user.id).child('Supplier_Name').get()
    city = db.child("suppliers").child(request.user.id).child('city').get()
    address = db.child("suppliers").child(request.user.id).child('Address').get()
    orders = db.child('suppliers').child(request.user.id).child('orders_recieved').get()
    return render(request, 'supplierauth/dashboard.html', {'name':name, 'city':city, 'address':address,'orders':orders})


def delete_supply(request, name):
    db = firebase.database()
    db.child('suppliers').child(request.user.id).child('available_supplies').child(name).remove()
    messages.success(request, f'successfully deleted {name}')
    return redirect('available_supplies')

def contact(request, name):
    name1 = name.split('-')
    name1 = " ".join(name1)
    name1 = name1.title()
    db = firebase.database()
    name = db.child("suppliers").child(request.user.id).child('Supplier_Name').get()
    city = db.child("suppliers").child(request.user.id).child('city').get()
    address = db.child("suppliers").child(request.user.id).child('Address').get()
    hospitalid = User.objects.get(first_name=name1).id
    print(name1, hospitalid)
    mychats = db.child('suppliers').child(request.user.id).child('chats').child(name1).get()

    chats = db.child("Hospitals").child(hospitalid).child("chats").child(request.user.first_name).get()

    return render(request, 'supplierauth/chat.html',
                  {'name': name, 'name1': name1, 'city': city, 'address': address, 'chats': chats, 'mychats':mychats})


def message(request,name):
    name1 = name.split('-')
    name1 = " ".join(name1)
    name1 = name1.title()
    db = firebase.database()
    if request.method=='POST':
        db.child("suppliers").child(request.user.id).child('chats').child(name1).push({'content':request.POST['message'], "time":time()})

    return HttpResponse("message send")

def confirm_order(request, name):
    name = name.split('-')
    name = " ".join(name)
    name = name.title()
    db = firebase.database()
    confirmedorder = db.child('suppliers').child(request.user.id).child('orders_recieved').child(name).get().val()
    db.child('suppliers').child(request.user.id).child('Confirmed_Orders').child(name).update(confirmedorder)
    db.child('suppliers').child(request.user.id).child('Confirmed_Orders').child(name).update({'order_status': ' confirmed'})

    db.child('suppliers').child(request.user.id).child('orders_recieved').child(name).remove()
    messages.success(request, f'successfully Confirmed Order from {name}')
    return redirect('confirmed_orders_list')

@csrf_protect
def change_status(request, name):
    print(request.POST)
    name = name.split('-')
    name = " ".join(name)
    name = name.title()
    db = firebase.database()
    db.child('suppliers').child(request.user.id).child('Confirmed_Orders').child(name).update({'order_status':request.POST.get('selectName', False)})
    return HttpResponse('successfully updated status')

def confirmed_orders_list(request):
    db = firebase.database()
    name = db.child("suppliers").child(request.user.id).child('Supplier_Name').get()
    city = db.child("suppliers").child(request.user.id).child('city').get()
    address = db.child("suppliers").child(request.user.id).child('Address').get()
    confirmedorders = db.child('suppliers').child(request.user.id).child('Confirmed_Orders').get()
    return render(request, 'supplierauth/confirmed_orders_list.html', {'name':name, 'city':city, 'address':address, 'confirmedorders':confirmedorders}, )

def available_supplies(request):
    data = {}
    db = firebase.database()
    name = db.child("suppliers").child(request.user.id).child('Supplier_Name').get()
    city = db.child("suppliers").child(request.user.id).child('city').get()
    address = db.child("suppliers").child(request.user.id).child('Address').get()
    if request.method=='POST':
        somevar = request.POST.getlist('checks[]')
        for i in somevar:
            data[i] = 'yes'
        db.child('suppliers').child(request.user.id).child('available_supplies').update(data)
        messages.success(request, 'Supplies Added Successfully ! ')
    availablesupplies = db.child('suppliers').child(request.user.id).child('available_supplies').get()
    return render(request, 'supplierauth/available_supplies.html', {'name':name, 'city':city, 'address':address, 'availablesupplies':availablesupplies})