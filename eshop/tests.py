from django.test import TestCase
from xmlrpc import client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
import time

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


class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(20)

    # @classmethod
    # def tearDownClass(cls):
    #     cls.selenium.quit()
    #     super().tearDownClass()

    def test_application(self):
        self.selenium.get('http://localhost:8000/login/')
        username_input = self.selenium.find_element_by_name("username")
        password_input = self.selenium.find_element_by_name("password")
        username_input.send_keys('test')
        password_input.send_keys('aaa')
        submit = self.selenium.find_element_by_name("login-submit")
        submit.send_keys(Keys.RETURN)
        self.selenium.find_element_by_xpath("//form[@id='form-id']//input[@name='product' and @value='28']").submit()

        time.sleep(10)
        is_customer = models.execute_kw(db, uid, odoopassword, 'sale.order',
                                        'search', [[['partner_id', '=', 'test']]])
        p = odoo.env['sale.order'].browse(is_customer)
        for pu in p:
            products = [line for line in pu.order_line]
            somme = 0
            for i in products:
                price =i.price_unit
                name = i.product_id.name
                somme = somme + price
                print('Name of the product : {},price : {}'.format(name,price))
            print('_____Somme_____', round(somme, 2))
        self.selenium.find_element_by_xpath("//input[@name='send_mail'] ").submit()


# class ProductModelTests(TestCase):
#
#     def test_product(self):


# is_customer = models.execute_kw(db, uid, odoopassword, 'sale.order',
#                                 'search', [[['partner_id', '=', 'test']]])
# order = [order for order in is_customer]
# p = odoo.env['sale.order'].browse(is_customer)
# for pu in p:
#     #print('--------purchase-------', pu.order_line.price_unit)
#     products = [line for line in pu.order_line]
#     print('----list product----', products)
#     somme = 0
#     # name =""
#     for i in products:
#         price =i.price_unit
#         name = i.product_id.name
#         somme = somme + price
#         print('----list product id----', i.id)
#         print('----name--: {} ---price--- : {}'.format(name,price))
#     print ('------Somme--------', round(somme,2))
# models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_cancel', order)
# models.execute_kw(db, uid, odoopassword,
#                   'sale.order', 'write', [order,
#                                           {'order_line': [(2, 234, False)]}])

# aa = models.execute_kw(db, uid, odoopassword, 'res.partner',
#                                'search', [[['name', '=', 'test']]])
# p = odoo.env['res.partner'].browse(aa)
# # print ('-----title------',p )
# x = models.execute_kw(db, uid, odoopassword,
#                    'res.partner.title', 'search_read', [[]], {'fields': ['name']})
# models.execute_kw(db, uid, odoopassword, 'res.partner.title', 'unlink', [8])
#
# print ('-----title------',x )
# is_customer = models.execute_kw(db, uid, odoopassword, 'sale.order',
#                                 'search', [[['partner_id', '=', 'test']]])
# facture_search = models.execute_kw(db, uid, odoopassword,
#                                    'account.invoice', 'search', [[['number', '=', 'INV/2018/0006']]])
# p = odoo.env['sale.order'].browse(is_customer)
# x = odoo.env['account.invoice'].browse(facture_search)
# d = {}
# # price = []
# for pu in p:
#     print('--------purchase-------', pu)
#     products = [line for line in pu.order_line]
#     print('----list product----', products)
#     for i in products:
#         print(i.name, i.price_unit)
#         d[(i.id,i.name,i.product_id.id)] = i.price_unit
#         print(d)
# for i in d.items():
#     x.write({'invoice_line_ids': [(0, 0,{
#                                     'name': i[0][1],
#                                     'product_id': i[0][2],
#                                     'account_id':1,
#                                     'price_unit':i[1],
#                                     })]})
