from django.test import TestCase
from xmlrpc import client
from django.contrib.auth.models import User
from .models import Profile
import odoorpc
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('odifydb', 'admin', 'admin')
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
        # Taxe = odoo.env['product.product']
        # order_ids = Taxe.search([('name','=','Carte graphique')])
        # for order in Taxe.browse(order_ids):
        #     print(order.lst_price)
        #     p = odoo.env['sale.order.line']
        #     p1= p.search([('product_id','=',int(order))])
        #     for x in p.browse(p1):
        #         print('________Taxe__________', x.price_unit)
        is_customer = models.execute_kw(db, uid, odoopassword, 'sale.order',
                                        'search', [[['partner_id', '=', 'test']]])
        p = odoo.env['sale.order'].browse(is_customer)
        for pu in p:
            #print('--------purchase-------', pu.order_line.price_unit)
            products = [line for line in pu.order_line]
            print('----list product----', products)
            somme = 0
            # name =""
            for i in products:
                price =i.price_unit
                name = i.product_id.name
                somme = somme + price
                print('----name--: {} ---price--- : {}'.format(name,price))
            print ('------Somme--------', round(somme,2))



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
