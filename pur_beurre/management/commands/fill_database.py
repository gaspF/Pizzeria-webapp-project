import requests
from pur_beurre.models import Categories, Product
from pur_beurre.forms import CategoriesForm
from string import punctuation, digits
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError, DataError


class Command(BaseCommand):
    def category_request_api(self):
        url = "https://fr.openfoodfacts.org/categories&json=1"
        request = requests.get(url)
        return request.json()

    def food_request(self, category):
        url = "https://fr.openfoodfacts.org/cgi/search.pl"
        params = {"action": "process",
                  "tagtype_0": "categories",
                  "tag_contains_0": "contains",
                  "tag_0": category.off_id,
                  "page_size": 1000,
                  "json": 1}

        request = requests.get(url, params)

        return request.json()

    def handle(self, *args, **options):
        self.stdout.write("Obtention des catégories d'Openfood Facts")
        categories_dict = self.category_request_api()
        self.stdout.write("Sauvegarde des catégories dans la base de données")
        self.save_cat_to_db(categories_dict)

        cat_amount = 10

        categories = Categories.objects.all()

        for category in categories:
            self.stdout.write("Récupération des aliments de la catégorie {0}".format(category.name))
            food_request_dict = self.food_request(category)
            self.stdout.write("Inscription dans la base de données des aliments de la catégorie {0}".format(category.name))
            self.save_food_to_db(food_request_dict)
            cat_amount -= 1

    def save_cat_to_db(self, request_dict):
        categories_list = request_dict["tags"][:3]
        for category in categories_list:
            name = self.request_cleaner(category["name"])
            url = category["url"]
            product_count = int(category["products"])
            off_id = category["id"]
            form_dict = {'name':name, 'product_count': product_count, 'url': url, 'off_id': off_id}

            entry = CategoriesForm(form_dict)

            if entry.is_valid():
                entry.save()

    def save_food_to_db(self, request_dict):
        food_list = request_dict["products"]
        for food in food_list:
            openfoodfacts_link = "https://fr.openfoodfacts.org/produit/" + food['code']
            try:
                name = self.request_cleaner(food["product_name"])
                brand = self.request_cleaner(food["brands"]).split(',')[0]
                itemcode = food["code"]
                description = food["ingredients_text"]
            except KeyError:
                pass
            try:
                image = food["image_url"]
            except KeyError:
                image = None
            try:
                nutriscore = self.request_cleaner(food["nutrition_grades"])
            except KeyError:
                nutriscore = "Z"

            food_categories = food["categories"].split(',')

            entry = self.add_to_db(name, brand, nutriscore, itemcode, description, openfoodfacts_link, image)

            self.add_relationship(food_categories, entry)

    def add_to_db(self, name, brand, nutriscore, description, openfoodfacts_link, itemcode, image):
        try:
            entry = Product()
            entry.name = name
            entry.description = description
            entry.brand = brand
            entry.nutriscore = nutriscore
            entry.openfoodfacts_link = openfoodfacts_link
            entry.itemcode = itemcode
            if image:
                entry.image = image
            entry.clean()
            entry.save()
            return entry
        except (IntegrityError, DataError):
            pass

    def add_relationship(self, food_category, entry):
        try:
            for food_category in food_category:
                food_category = self.request_cleaner(food_category)
                category = Categories.objects.get_or_create(name=food_category)[0]
                entry.categories.add(category)
        except(ValidationError, AttributeError):
            pass

    def request_cleaner(self, my_request):
        mr = my_request
        for character in punctuation:
            my_request = my_request.replace(character, '')
        for character in digits:
            my_request = my_request.replace(character, '')

        my_request = my_request.title().strip()
        return my_request

