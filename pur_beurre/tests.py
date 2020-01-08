from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock
from pur_beurre.management.commands import fill_database


from .models import *
from django.urls import reverse
from .views import UserSavedProductsList
from users.views import profile


class ProductModelTests(TestCase):
    def test_str(self):
        product = Product(name="Nom test", brand="marque test")
        self.assertIs(product.__str__(), "Nom test")


class CategoryModelTest(TestCase):
    def test_str(self):
        category = Categories(name="Test B")
        self.assertIs(category.__str__(), "Test B")


class ViewsTests(TestCase):

    def setUp(self):
        Product.objects.create(name='testname', brand='aubusson', image='http://imagetest.com')

    def test_homepage(self):
        response = self.client.get(reverse('pur-beurre-index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Du gras, oui,")

    def test_research(self):
        form_data = {'food': 'test'}
        response = self.client.get(reverse('pur-beurre-results'), form_data)
        html = response.content.decode('utf8')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "aubusson")
        self.assertInHTML('''<img src="http://imagetest.com" alt="food_image" class="sr-icons img-product">''', html)


class SubstituteViewTests(TestCase):
    def setUp(self):
        c = Categories.objects.create(name='testcat',
                                      url='http://imagetest.com',
                                      off_id='test')
        f1 = Product.objects.create(name='testname',
                                 brand='testbrand',
                                 nutriscore='B',
                                 image='http://imagetest.com',
                                 id=1)
        f1.categories.add(c)
        f2 = Product.objects.create(name='testnametwo',
                                 brand='testbrandtwo',
                                 nutriscore='A',
                                 image='http://imagetest.com',
                                 id=2)
        f2.categories.add(c)

    def test_get_request_got_results(self):
        response = self.client.get(reverse('pur-beurre-substitutes', args=[1]))
        html = response.content.decode('utf8')
        self.assertEqual(response.status_code, 200)
        self.assertInHTML('''<img class="sr-icons img-product" src="http://imagetest.com" alt="">''', html)
        self.assertTrue(html.startswith(''))


class UserLoggedIn(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(
            username='Patrick', email='patrick@yahoo.com', password='machin')

    def test_user_profile_page_logged_in(self):
        request = self.factory.get(reverse('profile'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "patrick@yahoo.com")

    def test_product_saved_logged_in(self):
        request = self.factory.get(reverse('saved-products'))
        request.user = self.user
        response = UserSavedProductsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Produits sauvés par Patrick")


class AnonUser(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = AnonymousUser()

    def test_anon_user_profile_redirect(self):
        request = self.factory.get(reverse('profile'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 302)

    def test_anon_user_saved_products_redirect(self):
        request = self.factory.get(reverse('saved-products'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 302)

    def test_anon_user_save_redirect(self):
        request = self.factory.get(reverse('pur-beurre-save'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 302)


class FillDatabase(TestCase):
    def setUp(self):
        self.command = fill_database.Command()

    @patch("requests.get")
    def test_cat_request(self, get):
        response = self.command.category_request_api()
        self.assertTrue(get.called)

    @patch('requests.get')
    def test_food_request(self, get):
        category = MagicMock()
        category.off_id = 'test'

        response = self.command.food_request(category)
        self.assertTrue(get.called)

    def test_cat_to_db(self):
        request_dict = {'tags': [
            {'name': 'test',
             'url': 'http://test.com',
             'products': 1,
             'id': 'testid'}
        ]}
        self.command.save_cat_to_db(request_dict)
        self.assertEqual(Categories.objects.count(), 1)

    def test_food_to_db(self):
        request_dict = {'products': [
            {'product_name': 'test',
             'code': '298392',
             'brands': 'testb',
             'nutrition_grades': 'B',
             'ingredients_text': 'testdescription',
             'url': 'http://test.com',
             'image_url': 'http://testimage.com',
             'categories': 'test1, test2'}
        ]}
        self.command.save_food_to_db(request_dict)
        f = Product.objects.first()
        self.assertEqual(Product.objects.count(), 1)

    def test_add_entry_to_db(self):
        name = 'testname'
        brand = 'testbrand'
        nutriscore = 'A'
        itemcode = '389289'
        image = 'http://www.test.com'
        url = 'http://testurl.com'
        openfoodfacts_link = 'http://offtestlink.com'

        self.command.add_to_db(name, brand, nutriscore, itemcode,
                               image, url, openfoodfacts_link)
        self.assertEqual(Product.objects.count(), 1)

    def test_func(self):
        save = self.get_object()
        if self.request.user == save.saved_by:
            return True
        return False