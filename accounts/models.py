from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.emails import send_account_activation_email
from products.models import Coupon, Products,ColorVariant,SizeVariant
# Create your models here.

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100,blank= True,null=True)
    profile_image = models.ImageField(upload_to="profile_images")
    
    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid = False , cart__user = self.user).count()
    
class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="cart")
    coupon = models.ForeignKey(Coupon , on_delete=models.SET_NULL,blank=True,null=True)
    is_paid = models.BooleanField(default=False)
    
    
    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price = []
        
        for i in cart_items:
            price.append(i.product.price)
            if i.color_variant:
                price.append(i.color_variant.price)
            if i.size_variant:
                price.append(i.size_variant.price)
        
        if self.coupon:
            if self.coupon.minimum_amount < sum(price):
                return sum(price) - self.coupon.discount_price
        
        return sum(price)
    
    
    

class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="cart_items")
    product = models.ForeignKey(Products, on_delete=models.SET_NULL,null=True,blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL,null=True,blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL,null=True,blank=True)
    
    def get_product_price(self):
        price = [self.product.price]
        
        if self.color_variant:
            price.append(self.color_variant.price)
        if self.size_variant:
            price.append(self.size_variant.price)
        
        return sum(price)
    

@receiver(post_save, sender=User)
def create_profile_and_send_email(sender, instance, created, **kwargs):
    try:
        if created:
            # Generate email token
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance,email_token = email_token)
            email = instance.email
            send_account_activation_email(email, email_token)
    except Exception as e:
            print(f"Error in sending email: {e}")