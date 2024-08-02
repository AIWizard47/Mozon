
from django.shortcuts import  render , redirect
from .models import  Products

# Create your views here.

def get_product(request,slug):

    try:
        product = Products.objects.get(slug=slug)
        cxt = {'product': product}
        if request.GET.get('size'):
            size = request.GET.get('size')
            print(size)
            price = product.get_product_price_by_size(size)
            cxt['selected_size'] = size
            cxt['updated_price'] = price
            print(price)
            print(cxt)
        return render(request, 'product/products.html', context=cxt)
    except Exception as e:
        # Optional: log the error
        print(e)
  
