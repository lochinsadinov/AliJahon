from django.db.models import Sum, Q, Count
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from django.views.generic import TemplateView, FormView

from apps.forms import OrderForm
from apps.models import District, AdminSite, Order, Thread, Visit, User
from apps.models import Product, Category


class HomeTemplateView(ListView):
    model = Product
    template_name = 'apps/site/home.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CategoryListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/site/maxsulotral.html'
    context_object_name = "products"

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        query = super().get_queryset()
        query = query.filter(category__slug=slug).all()
        return query

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['slug'] = self.kwargs.get('slug')
        return context




class AdminTemplateView(TemplateView):
    template_name = 'apps/site/admin.html'






class MerketCategoryListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/salesman/market.html'
    context_object_name = "products"

    def get_queryset(self):
        query = super().get_queryset()
        slug = self.kwargs.get('slug')
        q = self.request.GET.get("q")
        if slug == 'top':
            query = query.annotate(total_sold=Sum('orders__quantity')).order_by('-total_sold')
        elif slug != 'all':
            query = query.filter(category__slug=slug).all()
        elif q:
            query = query.filter(Q(name__icontains=q) | Q(description__icontains=q))    # incontains bu bizga izlap beradi ichida bormi dip
        return query

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['slug'] = self.kwargs.get('slug')
        return context






class CompetitionListView(ListView):
    query = User.objects.all()
    template_name = 'apps/site/konkurs.html'
    context_object_name = 'users'


    def get_queryset(self):
        # query = super().get_queryset()
        query = User.objects.all()
        query = query.annotate(
            sold=Count('threads__orders' , threads__orders__status=Order.StatusType.DELIVERED.value)).filter(sold__gt=0).order_by('-sold')
        return query

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args , **kwargs)
        context['site'] = AdminSite.objects.first()
        return context






class KangalarTemplateView(TemplateView):
    template_name = 'apps/site/kangalar.html'


# class ProductDetailView(DetailView, FormView):
#     form_class = OrderForm
#     queryset = Product.objects.all()
#     template_name = 'apps/site/product_detail.html'
#     slug_url_kwarg = 'slug'
#     context_object_name = "product"
#     success_url = reverse_lazy('order-success')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['site'] = AdminSite.objects.first()
#         return context
#
#     def form_valid(self, form):
#         data = form.cleaned_data
#         site = AdminSite.objects.first()
#         product = Product.objects.filter(slug=data.get('product')).first()
#         product.quantity -= 1
#         product.save()
#         all_amount = site.delivering_price + product.price
#         data['product'] = product
#         data['user'] = self.request.user
#         Order.objects.create(**data, all_amount=all_amount)  # malumotni databegsa saqlash formdan forma kelyapti
#         context = {
#             "product": product,
#             "site": site
#         }
#         return render(self.request, 'apps/order/success.html', context=context)
#
#     def form_invalid(self, form):
#         print(form)


class ProductDetailView(ListView, FormView):
    form_class = OrderForm
    queryset = Product.objects.all()
    template_name = 'apps/site/product_detail.html'
    context_object_name = "product"

    def get_queryset(self):
        query = super().get_queryset()
        thread_id = self.kwargs.get("thread_id")
        if thread_id:
            thread = Thread.objects.filter(id=thread_id).first()
            Visit.objects.create(thread = thread).save()
            product = thread.product
            query = query.filter(id=product.id).first()
        else:
            slug = self.kwargs.get("slug")
            query = query.filter(slug=slug).first()
        return query
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        thread_id = self.kwargs.get("thread_id")
        context['all_amount'] = context['product'].discount_price
        if thread_id:
            context['thread'] = Thread.objects.filter(id=thread_id).first()
            context['all_amount'] = context['product'].discount_price - context['thread'].discount_price
        context['site'] = AdminSite.objects.first()
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        site = AdminSite.objects.first()
        product = Product.objects.filter(slug=data.get('product')).first()
        product.quantity -= 1
        product.save()
        all_amount = site.delivering_price + product.price
        if data.get("thread"):
            thread = Thread.objects.filter(id=data.get("thread")).first()
            data['thread'] = thread
            all_amount -= thread.discount_price
        else:
            del data['thread']
        data['product'] = product
        data['user'] = self.request.user
        obj , create = Order.objects.get_or_create(**data, all_amount=all_amount)  # malumotni databegsa saqlash formdan forma kelyapti
        context = {
            "order": obj,
            "site": site ,
            "product_price" : product.discount_price
        }
        if data.get("thread"):
            context['product_price'] = product.discount_price - data.get('thread').discount_price
        return render(self.request, 'apps/order/success.html', context=context)

    def form_invalid(self, form):
        print(form)




class MahsulotlarListView(ListView):
    model = Product
    template_name = 'apps/site/maxsulotral.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['categories'] = Category.objects.all()
        context['slug'] = self.kwargs.get('slug')
        return context








def get_districts(request, region_id):
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse({'districts': list(districts)})


def search_view(request):
    query = request.GET.get('q' , '')
    if query:
        products = Product.objects.filter(name__icontains=query)
        data = [
            {
                "id" : product.id,
                "name" : product.name,
                "url" : product.get_absolute_url(),
                "image_url" : product.imege.url if product.image else "",
                "discount_price" : product.discount_price ,
                "salesman_price" : product.salesman_price ,
                "quantity" : product.quantity,
                "discount" : product.discount > 0
            }
            for product in products
        ]
    else :
        data = []
    return JsonResponse(data , safe=False)



