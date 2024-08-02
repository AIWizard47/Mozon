from django.shortcuts import render ,redirect
from django.contrib import messages
from django.contrib.auth import authenticate ,login ,logout
from django.contrib.auth.models import User

from products.models import Coupon, Products, SizeVariant
from .models import Cart, CartItems, Profile
from django.http import HttpResponseRedirect,HttpResponse
# Create your views here.

def login_page(request):
    
    if request.method=="POST":
        email = request.POST.get("username").strip()
        password = request.POST.get("password").strip()
        
        user_obj = User.objects.filter(username=email)
        if not user_obj.exists():
            messages.warning(request, 'Account Not found')
            return HttpResponseRedirect(request.path_info)
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'your account is not verified')
            return HttpResponseRedirect(request.path_info)
        
        user_obj = authenticate(username = email,password=password)
        if user_obj:
            login(request ,user_obj)
            return HttpResponseRedirect("/")
        
        
        messages.warning(request, 'Invalid credential')
        return HttpResponseRedirect(request.path_info)
    
    return render(request, 'accounts/login.html')

def register_page(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name").strip()
        last_name = request.POST.get("last_name").strip()
        email = request.POST.get("email").strip()
        password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirm_password").strip()
        
        if User.objects.filter(username=email).exists():
            messages.warning(request, 'Email already exists')
            return HttpResponseRedirect(request.path_info)
        
        if password != confirm_password:
            messages.warning(request, 'Passwords do not match')
            return HttpResponseRedirect(request.path_info)
        
        user_obj = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=email,
            email=email
        )
        user_obj.set_password(password)
        user_obj.save()
        
        messages.success(request, 'Email has been sent to your email address for verification')
        return HttpResponseRedirect(request.path_info)
    
    return render(request, 'accounts/register.html')

def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token=email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse("Invalid Email Token")   

def logout_view(request):
    logout(request)
    return redirect('/')

def add_to_cart(request,uid):
    
    variant = request.GET.get('variant')
    product = Products.objects.get(uid=uid)
    user = request.user     
    cart , _ = Cart.objects.get_or_create(user = user, is_paid = False)
    cart_item = CartItems.objects.create(cart = cart,product = product,)
    
    if variant:
        variant = request.GET.get('variant')
        size_variant = SizeVariant.objects.get(size_name = variant)
        cart_item.size_variant = size_variant
        cart_item.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_cart(request,cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
        
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def cart(request):
    cart_obj = Cart.objects.get(is_paid = False , user = request.user)
    if request.method=="POST":
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains = coupon)
        
        if not coupon_obj.exists():
            messages.warning(request , 'Invalid Coupon.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.coupon:
            messages.warning(request , 'Coupon already exists.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total()<coupon_obj[0].minimum_amount:
            messages.warning(request , f'At least Shop Above {coupon_obj[0].minimum_amount}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj[0].is_expired:
            messages.warning(request , 'Coupon is Expired.')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.warning(request , 'Coupon Applied.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
    context ={'cart' : cart_obj}
    return render(request,'cart/cart.html',context = context)

def remove_coupon(request , cart_uid):
    cart_obj = Cart.objects.get(uid = cart_uid)
    cart_obj.coupon = None
    cart_obj.save()
    messages.warning(request , 'Coupon Removed.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))