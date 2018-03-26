from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from xmlrpc import client
from django.contrib.auth import authenticate, login
from django_odoo_auth.odoo_auth.models import OdooUser
from django.contrib.auth.models import User
from .forms import UserForm, ProfileForm
from django.views.generic import View
from django.contrib import messages
import base64
import json
from urllib.request import urlopen
import xml.etree.ElementTree as ElementTree


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
                               {'fields': ['id', 'test', 'description', 'image_medium', 'name', 'standard_price']})

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
            print('_________product_____', product)
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
            else:

                # order_line =models.execute_kw(db, uid, odoopassword,
                # 		  'sale.order', 'search',
                # 		  [[['partner_id', '=', request.user.username]]])
                for order in is_customer:
                    models.execute_kw(db, uid, odoopassword,
                              'sale.order', 'write', [[order],
                                                      {'order_line': [(0, 0, {'product_id': int(product)})]}])
                #  request.POST.get(record[0]['name'],False)

    return render(request, 'eshop/home.html',
        		  {'product': record[:8], 'category': category, 'product_range': record[12:16], })

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












