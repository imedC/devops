from django.test import TestCase
from xmlrpc import client
from django.contrib.auth.models import User
from .models import Profile

url = 'http://localhost:8069'
db = 'odifydb'
odooname = 'admin'
odoopassword = 'admin'
common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, odooname, odoopassword, {})
models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
# Create your tests here.
class ProductModelTests(TestCase):

    def test_product(self):
        record = models.execute_kw(db, uid, odoopassword,
                                   'product.product', 'search_read', [[['create_uid', '=', 1]]],
                                   {'fields': ['id', 'description', 'name', 'standard_price']})

        #print ('____User____ :', request.user)
        print ('____product___ :', record[12:16])

# class ProfileTestCase(TestCase):
#
#     def setUp(self):
#         self.credentials = {
#             'username': 'testuser',
#             'password': 'secret'}
#         User.objects.create_user(**self.credentials)
#
#     def test_login(self):
#         # send login data
#         response = self.client.post('/login/', self.credentials, follow=True)
#         # should be logged in now
#         print(self.assertTrue(response.context['user'].is_authenticated))
