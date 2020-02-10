from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth.views import LoginView
from django.test import RequestFactory, TestCase
from unittest.mock import patch, MagicMock
from pur_beurre.management.commands import fill_database
from .models import *
from django.urls import reverse
from .views import UserSavedProductsList, SaveDelete
from users.views import profile, register


class ProductModelTests(TestCase):
    """ Testing product name
                                """
    def test_str(self):
        product = Product(name="Nom test", brand="marque test")
        self.assertIs(product.__str__(), "Nom test")


class CategoryModelTest(TestCase):
    """ Testing category name
                                    """
    def test_str(self):
        category = Categories(name="Test B")
        self.assertIs(category.__str__(), "Test B")


class ViewsTests(TestCase):
    def setUp(self):
        """ Setting up a new test product for TestCase
                                        """
        Product.objects.create(name='testname', brand='aubusson', image='http://imagetest.com')

    def test_homepage(self):
        """ Testing homepage view. The test must return a correct 200 code and contains some specifics strings characters
                                        """
        response = self.client.get(reverse('pur-beurre-index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Du gras, oui,")

    def test_research(self):
        """ Testing research view. The test must return a correct 200 code and contains some specifics strings characters
                                                """
        form_data = {'food': 'test'}
        response = self.client.get(reverse('pur-beurre-results'), form_data)
        html = response.content.decode('utf8')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "aubusson")
        self.assertInHTML('''<img src="http://imagetest.com" alt="food_image" class="sr-icons img-product">''', html)

    def test_legal(self):
        """ Testing legal view. The test must return a correct 200 code and contains some specifics strings
                                                """
        response = self.client.get(reverse('legal_notices'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hébergeur")


class SubstituteViewTests(TestCase):
    def setUp(self):
        """ Setting up two new test products, and one category for TestCase
                                                """
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
        """ Testing if the substitute view display an appropriate product
                                                """
        response = self.client.get(reverse('pur-beurre-substitutes', args=[1]))
        html = response.content.decode('utf8')
        self.assertEqual(response.status_code, 200)
        self.assertInHTML('''<img class="sr-icons img-product" src="http://imagetest.com" alt="">''', html)
        self.assertTrue(html.startswith(''))


class UserLoggedIn(TestCase):
    def setUp(self):
        """ Setting up a new test product and a new user for TestCase, and creating an association between them
                                                """
        self.factory = RequestFactory()
        self.product = Product.objects.create(name='testname',
                                              brand='testbrand',
                                              nutriscore='B',
                                              image='http://imagetest.com',
                                              id=1
                                              )
        self.user = User.objects.create(
            username='Patrick',
            email='patrick@yahoo.com',
            password='machin'
        )
        self.save = SavedProduct.objects.create(saved_by=self.user, saved_product=self.product)

    def test_delete_func(self):
        """ Testing delete function
                                              """
        request = self.client.get(reverse('save-delete', args=[1]), follow=True)
        self.assertContains(request, 'Suppression de produit')

    """
    def test_response_delete_func(self):
        response = self.client.post(reverse('save-delete', args=[1]), follow=True)
        self.assertRedirects(response, reverse('saved-products'), status_code=response.status_code)
        """

    def test_user_profile_page_logged_in(self):
        """ Testing if the logged user get the correct information about himself on profile view
                                                """
        request = self.factory.get(reverse('profile'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "patrick@yahoo.com")

    def test_product_saved_logged_in(self):
        """ Testing if the logged user get the correct information about his favorites products on saved products view
                                                        """
        request = self.factory.get(reverse('saved-products'))
        request.user = self.user
        response = UserSavedProductsList.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Produits sauvés par Patrick")
        self.assertContains(response, "testname")


class AnonUser(TestCase):
    def setUp(self):
        """ Setting up an anonymous user for TestCase
                                                        """
        self.factory = RequestFactory()
        self.user = AnonymousUser()

    def test_anon_user_profile_redirect(self):
        """ Testing the redirection to a 302 error when the anonymous user try to get his profile
                                                                """
        request = self.factory.get(reverse('profile'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 302)

    def test_anon_user_saved_products_redirect(self):
        """ Testing the redirection to a 302 error when the anonymous user try to get his saved products
                                                                        """
        request = self.factory.get(reverse('saved-products'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 302)

    def test_anon_user_save_redirect(self):
        """ Testing the redirection to a 302 error when the anonymous user try to save a product
                                                                        """
        request = self.factory.get(reverse('pur-beurre-save'))
        request.user = self.user
        response = profile(request)
        self.assertEqual(response.status_code, 302)

    def test_anon_user_register(self):
        """ Testing the correct displaying of the register page when the anonymous user try to create a new account
                                                                        """
        request = self.factory.get(reverse('register'))
        request.user = self.user
        response = register(request)
        self.assertEqual(response.status_code, 200)


class FillDatabase(TestCase):
    def setUp(self):
        """ Setting up a script to test for TestCase
        """
        self.command = fill_database.Command()

    @patch("requests.get")
    def test_cat_request(self, get):
        """ Testing if the request is correctly called by a get request
                """
        response = self.command.category_request_api()
        self.assertTrue(get.called)

    @patch('requests.get')
    def test_food_request(self, get):
        """ Testing if the product request is correctly called by a get request
                        """
        category = MagicMock()
        category.off_id = 'test'

        response = self.command.food_request(category)
        self.assertTrue(get.called)

    def test_cat_to_db(self):
        """ Testing if the category data is correctly saved into the database
                        """
        request_dict = {'tags': [
            {'name': 'test',
             'url': 'http://test.com',
             'products': 1,
             'id': 'testid'}
        ]}
        self.command.save_cat_to_db(request_dict)
        self.assertEqual(Categories.objects.count(), 1)

    def test_food_to_db(self):
        """ Testing if the food data is correctly saved into the database
                                """
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
        """ Testing if the product data entry is created for the database
                                """
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



