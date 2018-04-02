from django.shortcuts import render, redirect, render_to_response, HttpResponseRedirect, reverse
from xmlrpc import client
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import UserForm, ProfileForm
from django.views.generic import View
from django.contrib import messages
import base64
import xml.etree.ElementTree as ElementTree
# import oerplib
import odoorpc


url = 'http://localhost:8069'
db = 'odifydb'
odooname = 'admin'
odoopassword = 'admin'
# returns user objects if credentials are correct
common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, odooname, odoopassword, {})
models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))

def home(request):
    record = models.execute_kw(db, uid, odoopassword,
                               'product.product', 'search_read', [[['create_uid', '=', 1]]],
                               {'fields': ['id','description', 'image_medium', 'name', 'standard_price']})

    category = models.execute_kw(db, uid, odoopassword,
                                 'product.product', 'search_read', [[['create_uid', '=', 1]]],
                                 {'fields': ['categ_id', 'name', ]})
    x = [x.get('id', ) for x in record]
    # print '____fff__', x
    print ('______username:_______',request.user)
    search_user_id = models.execute_kw(db, uid, odoopassword,
                                       'res.partner', 'search',
                                       [[['name', '=', request.user.username]]])

    print ('______quotation:_______',search_user_id)
    print ('record:_______',record[6]['id'])
    for q in search_user_id:
        if request.method == "POST":
            product = request.POST.get('product')
            #record1 = request.POST.get(record)
            print('_________product_____', product)
            #print('_________product_____', record1)
            is_customer = models.execute_kw(db, uid, odoopassword, 'sale.order',
                                    'search', [[['partner_id', '=', request.user.username]]])
            if not is_customer:
                models.execute_kw(db, uid, odoopassword,
                          'sale.order', 'create', [{'partner_id': q}])
                customer = models.execute_kw(db, uid, odoopassword, 'sale.order',
                                  'search', [[['partner_id', '=', request.user.username]]])
                for order in customer:
                    models.execute_kw(db, uid, odoopassword,
                                  'sale.order', 'write', [[order],
                                                          {'order_line': [(0, 0, {'product_id': int(product)})]}])
                    models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_confirm', [order])
            else:

                # order_line =models.execute_kw(db, uid, odoopassword,
                # 		  'sale.order', 'search',
                # 		  [[['partner_id', '=', request.user.username]]])
                for order in is_customer:
                    confirm = models.execute_kw(db, uid, odoopassword,
                              'sale.order', 'write', [[order],
                                                      {'order_line': [(0, 0, {'product_id': int(product)})]}])
                    print ('--------confirm-------',confirm)
                models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_confirm', [order])
                request.session['order'] = order
                request.session['product'] = product
                print (order)
                return redirect('eshop:send')
    return render(request, 'eshop/home.html',
        		  {'product': record[:8], 'category': category, 'product_range': record[12:16], })

def send_mail(request):
    odoo = odoorpc.ODOO('localhost', port=8069)
    print(odoo.db.list())
    odoo.login('odifydb', 'admin', 'admin')

    order = request.session['order']
    product = request.session['product']
    print('-------------record------------', product)
    if request.method == "POST":
        models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_quotation_send', [[order]])
        print('order', order)
        search_user_id = models.execute_kw(db, uid, odoopassword,
                                           'res.partner', 'search',
                                           [[['name', '=', request.user.username]]])
        print('search_user_id', search_user_id)
        # TODO
        # Search for mail template
        template_id = models.execute_kw(db, uid, odoopassword,
                                        'mail.template', 'search',
                                        [[['name', 'ilike', 'Sales Order - Send by Email']]])
        print('-----template_id-------', template_id)
        print('-----order-------', order)
        # Use send_mail function
        # template = models.execute_kw(db, uid, odoopassword, 'mail.template', 'browse',[[order]])

        Partner = odoo.env['mail.template'].browse(template_id).send_mail(order, force_send=True)
        print('-----------partner-------------', Partner)
        return HttpResponseRedirect("/send/")
    purchase = models.execute_kw(db, uid, odoopassword,
                                           'sale.order', 'search',
                                           [[['name','=','SO077']]])
    p = odoo.env['sale.order'].browse(purchase)
    for pu in p:
        print('--------purchase-------', pu.order_line.price_unit)
        products = [line for line in pu.order_line]
        print(products)
        x = 0
        y=0
        for i in products:
            x = x + (i.price_unit)
            x = round(x,2)
            print('---------somme price_unit----', x)
        for i in products:
            y = y + (i.product_id.lst_price)
            print('---------somme lst_price----', y)
        return render(request, 'eshop/send.html', {'product': products, 'somme':x,'lst_price':y})
    return render(request,'eshop/send.html')
class UserFormView(View):

	form_class = UserForm
	template_name = 'eshop/register.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	# process from data

	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():

			user = form.save(commit=False)

			# cleaned data

			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			email = form.cleaned_data['email']
			user.set_password(password)
			user.save()
			user_id = models.execute_kw(db, uid, odoopassword, 'res.partner', 'create',
										[{'name': username, 'login': email}])
			print(user_id)
			user = authenticate(username=username, password=password)
			messages.add_message(request, messages.SUCCESS, 'Your account were successfully created.')

			if user is not None:

				if user.is_active:
					login(request, user)
					#base_template_name = 'base.html'
					return render(request, 'eshop/home.html', {})

		return render(request, self.template_name, {'form': form})


def update_profile(request,username):
	#user = User.objects.get(username=username)
	if request.method == 'POST':
		profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
		if profile_form.is_valid():
			profile_form.save()
			messages.success(request, ('Your profile was successfully updated!'))
			search_user_id = models.execute_kw(db, uid, odoopassword,
											   'res.partner', 'search',
											   [[['name', '=', username]]])
			#print('___', search_user_id)
			img = '/home/imed/Desktop/testpfe/media/'+str(request.user.profile.avatar)
			image_read = image.read()
			image_64_encode = base64.encodestring(image_read).decode("utf-8")
			print('______________',type(image_64_encode))
			for i in search_user_id:
				models.execute_kw(db, uid, odoopassword, 'res.partner', 'write', [[i], {'image': image_64_encode}])
			return redirect('eshop:home')

		else:
			messages.error(request, ('Please correct the error below.'))
	else:
		profile_form = ProfileForm(instance=request.user.profile)
	return render(request, 'eshop/edit_profile.html', {
		'profile_form': profile_form })




def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)

				return render(request, 'eshop/home.html', {})
			else:
				return render(request, 'eshop/login.html', {'error_message': 'Your account has been disabled'})
		else:
			return render(request, 'eshop/login.html', {'error_message': 'Invalid login'})
	return render(request, 'eshop/login.html')


def chekout(request):
	if request.method == 'POST':
		print (request.method)
	context = {}
	template = 'eshop/chekout.html'
	return render(request,template,context)












