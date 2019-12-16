import logging
from django.utils.decorators import method_decorator
from .models import Product, SavedProduct
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.views.generic import ListView
from django.views import View
from django.shortcuts import render
from pur_beurre.models import Product
from pur_beurre.forms import FoodRequestForm
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

class Index(View):
    form = FoodRequestForm
    template_name = "pur_beurre/pages/index.html"

    def get(self, request):
        form = self.form
        context_dict = {'form' : form}
        return render(request, self.template_name, context_dict)


class Legal(View):
    template_name = "pur_beurre/pages/legal_notices.html"

    def get(self, request):
        return render(request, self.template_name)


class Results(View):
    form = FoodRequestForm
    template_name = "pur_beurre/pages/results.html"

    def get(self, request):
        form = self.form(request.GET)
        page = request.GET.get('page')
        if form.is_valid():
            research = form.cleaned_data.get('food')
            queryset = Product.objects.filter(name__icontains=research)

            if queryset.count() <= 0:
                return render(request, self.template_name)
            else:
                new_queryset = []
                for list in self.chunks(queryset, 3):
                    new_queryset.append(list)

                paginator = Paginator(new_queryset, 10)
                foods = paginator.get_page(page)
                context_dict = {"queryset": foods}

                return render(request, self.template_name, context_dict)

    @staticmethod
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


class Substitutes(View):
    template_name = 'pur_beurre/pages/substitutes.html'

    def get(self, request, id):
        page = request.GET.get('page')
        food = Product.objects.get(id=id)
        basefood = Product.objects.get(id=id)
        categories = food.categories.all().order_by('id')
        nutriscore_list = self.nutriscore_list(food.nutriscore)

        queryset = Product.objects.filter(categories=categories[0]).filter(
            nutriscore__in=nutriscore_list).exclude(id=id)

        for category in categories[1:5]:
            query = Product.objects.filter(categories=category).filter(
                nutriscore__in=nutriscore_list).exclude(id=id)
            queryset = queryset.intersection(query)

        if queryset.count() == 0:
            return render(request, self.template_name)
        else:
            new_queryset = []
            for list in self.chunks(queryset, 3):
                new_queryset.append(list)

            paginator = Paginator(new_queryset, 10)
            foods = paginator.get_page(page)
            context_dict = {"queryset": foods,
                            "research": food,
                            "basefood": basefood}
            return render(request, self.template_name, context_dict)

    @staticmethod
    def nutriscore_list(nutriscore):
        if nutriscore == 'A':
            return ['A']
        elif nutriscore == 'B':
            return ['A']
        elif nutriscore == 'C':
            return ['A', 'B']
        elif nutriscore == 'D':
            return ['A', 'B', 'C']
        elif nutriscore == 'E':
            return ['A', 'B', 'C', 'D']
        elif nutriscore == 'Z':
            return ['A', 'B', 'C', 'D', 'E']

    @staticmethod
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


class Food(View):
    """Return the template for a single product"""
    template_name = 'pur_beurre/pages/food.html'

    def get(self, request, id):
        food = Product.objects.get(id=id)

        context_dict = {'food': food}

        return render(request, self.template_name, context_dict)


class SaveProduct(View):
    template_name = 'pur_beurre/pages/save.html'

    @method_decorator(login_required)
    def post(self, request):
        food_num = request.POST['food_id']
        food = Product(id=food_num)
        foodr = Product.objects.get(id=food_num)
        context_dict = {'foodr': foodr}

        try:
            save = SavedProduct(saved_by=request.user, saved_product=food)
            save.save()
            print(foodr.name)
        except IntegrityError as error:
            print(error)
            already_saved = "Ce produit figure déjà dans vos favoris"
            context_dict = {'foodr': foodr,
                            'already_saved': already_saved}

        return render(request, "pur_beurre/pages/save.html", context_dict)

    @staticmethod
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]


class UserSavedProductsList(ListView):
    model = SavedProduct
    template_name = 'pur_beurre/pages/saved_products.html'
    paginate_by = 6

    def get(self, request):
        page = request.GET.get('page')
        queryset = SavedProduct.objects.select_related('saved_product').filter(saved_by=request.user)

        if queryset.count() <= 0:
            return render(request, self.template_name)
        else:
            new_queryset = []
            for list in self.chunks(queryset, 3):
                new_queryset.append(list)

            paginator = Paginator(new_queryset, 10)
            foods = paginator.get_page(page)
            context_dict = {"queryset": foods}

            return render(request, self.template_name, context_dict)

    @staticmethod
    def chunks(l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]



