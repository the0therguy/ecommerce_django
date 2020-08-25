# Create your views here.
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def register_page(request):
    if request.user.is_authenticated:
        return redirect("store")
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, "Account was created " + user)
                return redirect('login')

        context = {'form': form}
        return render(request, 'store/register.html', context)


def login_page(request):
    if request.user.is_authenticated:
        return redirect("store")
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("store")
            else:
                messages.info(request, "messages and password is incorrect")
                return render(request, 'store/login.html')
        context = {}
        return render(request, 'store/login.html', context)


def logout_page(request):
    return redirect("login")


def store(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def update_item(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_crete(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse({'Item was added': 'Done'}, safe=False)


def process_order(request):
    post = {'Payment complete': 'done'}
    transaction_id = datetime.datetime.now().timestamp()

    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    if total == float(order.get_cart_total):
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],

        )
    return JsonResponse(post, safe=False)
