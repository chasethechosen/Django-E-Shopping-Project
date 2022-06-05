from unicodedata import category
from django.shortcuts import render,redirect ,HttpResponse
from django.views import View
from requests import request
from .models import *
from .forms import CustomerProfileForm, CustomerRegistrationForm, LoginForm, CustomerProfileForm
# Message Framework sucess message
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# login customer auth in urls



class ProductView(View):
    def get(self,request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        return render(request,'app/home.html',
        {
            'topwears':topwears,
            'bottomwears':bottomwears,
            'mobiles':mobiles
        }) 

class ProductDetailView(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product': product, 'item_already_in_cart': item_already_in_cart})
       



#  CART
    
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    print('prod_id',product_id)
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('showcart')

    
@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        print('cart',cart)
        amount = 0.0
        shipping_amount = 100.0
        total_amount = 0.0
        # list-comprehension
        # first obj  stored in 2nd p and if user is same as login user then obj is moved in first p( so current login user products we will get)
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        print('cart_product',cart_product)
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                totalamount = amount + shipping_amount
            return render(request, 'app/addtocart.html', {'carts': cart, 'totalamount': totalamount, 'amount': amount,'totalitem': totalitem})
        else:
            return render(request, 'app/emptycart.html')

def plus_cart(request):
    if request.method == 'GET':
        # prod-id from js(ajax)
        prod_id = request.GET['prod_id']

        # using get to extract single object
        #     Encapsulate filters as objects that can then be combined logically (using
        # `&` and `|`).
   
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()

        amount = 0.0
        shipping_amount = 100.0
        total_amount = 0.0
        # copy from up
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            totalamount = amount + shipping_amount
# Passing below BY JSON response (import it)
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)

def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        # print('iddddddddddddddddddddddddddddddddddddddddddddddddd',prod_id)

        # using get to extract single object
        c = Cart.objects.getr(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()

        amount = 0.0
        shipping_amount = 100.0
        total_amount = 0.0
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)
    
@login_required
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']

        # using get to extract single object
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()

        amount = 0.0
        shipping_amount = 100.0
        total_amount = 0.0
        # list-comprehension
        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]

        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shipping_amount
        }
        return JsonResponse(data)




def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': add, 'active': 'btn-primary'})

def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placed': op})



def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category="M")
    elif data =='oppo' or data == 'samsung':
        mobiles = Product.objects.filter(category="M").filter(brand=data)
    elif data =='below':
        mobiles = Product.objects.filter(category="M").filter(discounted_price__lt=40000)
    elif data =='above':
        mobiles = Product.objects.filter(category="M").filter(discounted_price__gt=50000)
    return render(request, 'app/mobile.html',{'mobiles':mobiles})

def laptop(request, data=None):
    if data == None:
        laptop = Product.objects.filter(category='L')
    elif data == 'ASUS' or data == 'Apple':
        laptop = Product.objects.filter(category='L').filter(brand=data)
    elif data == 'above':
        laptop = Product.objects.filter(
            category='L').filter(discounted_price__gt=50000)
    elif data == 'below':
        laptop = Product.objects.filter(
            category='L').filter(discounted_price__lt=50000)

    return render(request, 'app/laptop.html', {'laptop': laptop})

def topwear(request, data=None):
    if data == None:
        topwear = Product.objects.filter(category='TW')
    elif data == 'meow' or data == 'meko':
        topwear = Product.objects.filter(category='TW').filter(brand=data)
    elif data == 'above':
        topwear = Product.objects.filter(
            category='TW').filter(discounted_price__gt=500)
    elif data == 'below':
        topwear = Product.objects.filter(
            category='TW').filter(discounted_price__lt=500)

    return render(request, 'app/topwear.html', {'topwear': topwear})


def bottomwear(request, data=None):
    if data == None:
        bottomwear = Product.objects.filter(category='BW')
    elif data == 'meow' or data == 'meko':
        bottomwear = Product.objects.filter(category='BW').filter(brand=data)
    elif data == 'above':
        bottomwear = Product.objects.filter(
            category='BW').filter(discounted_price__gt=500)
    elif data == 'below':
        bottomwear = Product.objects.filter(
            category='BW').filter(discounted_price__lt=500)

    return render(request, 'app/bottomwear.html', {'bottomwear': bottomwear})



def login(request):
 return render(request, 'app/login.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(
                request, 'Congratulations!! Registered Successfully')
            form.save()
        return render(request, 'app/customerregistration.html', {'form': form})

#  PAYMENT
    
@login_required       
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    totalamount = 0.0

    cart_product = [p for p in Cart.objects.all() if p.user == request.user]

    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        totalamount = amount + shipping_amount
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'app/checkout.html', {'add': add, 'totalamount': totalamount, 'cart_items': cart_items, 'totalitem': totalitem})

@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)

    for c in cart:
        OrderPlaced(user=user, customer=customer,
                    product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect("orders")

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    def get(self,request):
        form = CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form,'active': 'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality,
                           city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(
                request, 'Congratulations Profile Updated Successfully!!')
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})
     


def buy_now(request):
 return render(request, 'app/buynow.html')

def profile(request):
 return render(request, 'app/profile.html')