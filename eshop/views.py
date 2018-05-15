from django.shortcuts import render, redirect, render_to_response, HttpResponseRedirect, reverse
from xmlrpc import client
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserForm, ProfileForm
from django.views.generic import View
from django.contrib import messages
import base64
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# import oerplib
import odoorpc
from django.conf import settings


url = 'http://localhost:8069'
db = 'odifydb'
odooname = 'admin'
odoopassword = 'admin'
odoo = odoorpc.ODOO('localhost', port=8069)
odoo.login('odifydb', 'admin', 'admin')
# returns user objects if credentials are correct
common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, odooname, odoopassword, {})
models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))

def home(request):
    record = models.execute_kw(db, uid, odoopassword,
                               'product.product', 'search_read', [[['create_uid', '=', 1]]],
                               {'fields': ['id','description', 'image_medium', 'name', 'lst_price']})

    category = models.execute_kw(db, uid, odoopassword,
                                 'product.product', 'search_read', [[['create_uid', '=', 1]]],
                                 {'fields': ['categ_id', 'name', ]})
    x = [x.get('id', ) for x in record]
    # print '____fff__', x
    print ('______username:_______',request.user)
    search_user_id = odoo.env['res.partner'].search([['name', '=', request.user.username]])

    customer_fac = odoo.env['account.invoice'].search([['number','=', 'INV/2018/0005']])
    x = odoo.env['account.invoice'].browse(customer_fac)
    for  i in x:
        print(i.invoice_line_ids)
    aa = x.read(['invoice_line_ids'])
    # x.write({'invoice_line_ids': [(0, 0, {'name':'[CARD] Graphics Card','account_id': 1,'price_unit': 500 })]})


    print ('______quotation:_______',search_user_id)
    print ('record:_______',record[6]['id'])
    for q in search_user_id:
        if request.method == 'POST':
            product = request.POST.get('product')
            print('_________product_____', product)
            product_name = request.POST.get('product_name')
            #print('_________product_____', record1)
            is_customer = odoo.env['sale.order'].search([['partner_id', '=', request.user.username]])
            facture_search = odoo.env['account.invoice'].search([['partner_id', '=', request.user.username]])

            if not is_customer:
                models.execute_kw(db, uid, odoopassword,
                          'sale.order', 'create', [{'partner_id': q}])
                customer = odoo.env['sale.order'].search([['partner_id', '=', request.user.username]])
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
                    print('--------product_name', product)
                    confirm = models.execute_kw(db, uid, odoopassword,
                              'sale.order', 'write', [[order],
                                                      {'order_line': [(0, 0, {'product_id': int(product)})]}])

                    customer_fac = models.execute_kw(db, uid, odoopassword,
                                                     'account.invoice', 'search', [[['number', '=', 'INV/2018/0006']]])
                    x = odoo.env['account.invoice'].browse(customer_fac)
                    for i in x:
                        print('-------invoice------',i.invoice_line_ids.name)
                    aa = x.read(['invoice_line_ids'])
                    print('-----aaa-----', aa)
                    # x.write({'invoice_line_ids': [(0, 0, {'name':int(product).name,'account_id': 1,'price_unit': 500 })]})
                    models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_confirm', [order])
                    request.session['order'] = order
                    request.session['product'] = product
                # print (order)
            return redirect('eshop:send')
    return render(request, 'eshop/home.html',
                  {'product': record, 'category': category, 'product_range': record[12:16], })



def send_mail(request):
    odoo = odoorpc.ODOO('localhost', port=8069)
    print(odoo.db.list())
    odoo.login('odifydb', 'admin', 'admin')
    facture_search = models.execute_kw(db, uid, odoopassword,
                                       'account.invoice', 'search', [[['partner_id', '=', request.user.username]]])

    is_customer = odoo.env['sale.order'].search([['partner_id', '=', request.user.username]])
    order = [order for order in is_customer]
    facture = [facture for facture in facture_search]
    print('-----is customer----', order)
    #order = request.session['order']
    # product = request.session['product']
    # print('-------------record------------', product)
    #if request.method == 'POST':
    if 'send_mail' in request.POST:
        # models.execute_kw(db, uid, odoopassword,
        #                   'account.invoice', 'create', [{'partner_id': request.user.username}])

        models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_quotation_send', order)
        print('order', order)
        search_user_id = odoo.env['res.partner'].search([['name', '=', request.user.username]])
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
        for o in order:
            Partner = odoo.env['mail.template'].browse(template_id).send_mail(o, force_send=True)
            print('-----------partner-------------', Partner)
            return HttpResponseRedirect("/send/")
    purchase = models.execute_kw(db, uid, odoopassword,
                                           'sale.order', 'search',
                                           [[['name','=','SO077']]])
    p = odoo.env['sale.order'].browse(is_customer)
    for pu in p:
        # print('--------purchase-------', pu.order_line.price_unit)
        products = [line for line in pu.order_line]
        # print('----list product----', products)
        x = 0
        y = 0
        for i in products:
            x = x + (i.price_unit)
            x = round(x, 2)
            # print('---------somme price_unit----', x)
        for i in products:
            y = y + (i.product_id.lst_price)
            # print('---------somme lst_price----', y)

        if 'delete' in request.POST:
            remove = request.POST.get('del')
            remove_price = request.POST.get('del_p')
            remove_name = request.POST.get('del_n')
            print('---remove-------', remove)
            models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_cancel', order)
            models.execute_kw(db, uid, odoopassword,
                                  'sale.order', 'write', [order,
                                                          {'order_line': [(2, int(remove))]}])
            models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_draft', order)
            models.execute_kw(db, uid, odoopassword, 'sale.order', 'action_confirm', order)
            return HttpResponseRedirect("/send/")
        return render(request, 'eshop/send.html', {'product': products, 'somme':x,'lst_price':y})
    return render(request,'eshop/send.html')




def products(request):
    category = models.execute_kw(db, uid, odoopassword,
                                 'product.product', 'search_read', [[['create_uid', '=', 1]]],
                                 {'fields': ['id', 'description', 'image_medium', 'name', 'lst_price', ]})

    # x = [x.get('name','image_medium') for x in record]
    # y = [y.get('name') for y in record]
    x = [x.get('description', ) for x in category]
    print ('____fff__', x)
    # print '___IDS____', category
    page = request.GET.get('page', 1)

    paginator = Paginator(category, 9)
    try:
        cat = paginator.page(page)
    except PageNotAnInteger:
        cat = paginator.page(1)
    except EmptyPage:
        cat = paginator.page(paginator.num_pages)
    #text = _("All Products")

    return render(request, 'eshop/products.html',
                  {'category': category, 'cat': cat})


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
                                        [{'name': username, 'email': email}])
            print(user_id)
            user = authenticate(username=username, password=password)
            messages.add_message(request, messages.SUCCESS, 'Your account were successfully created.')

            if user is not None:

                if user.is_active:
                    login(request, user)
                    #base_template_name = 'base.html'
                    return redirect('eshop:edit_profile')

        return render(request, self.template_name, {'form': form})


def update_profile(request):
    odoo = odoorpc.ODOO('localhost', port=8069)
    odoo.login('odifydb', 'admin', 'admin')
    #user = User.objects.get(username=username)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, ('Your profile was successfully updated!'))
            search_user_id = models.execute_kw(db, uid, odoopassword,
                                               'res.partner', 'search',
                                               [[['name', '=', request.user.username]]])
            #print('___', search_user_id)

            img = '/home/imed/Desktop/devops/media/'+str(request.user.profile.avatar)
            with open(img, 'rb') as img:
                image_read = img.read()
                image_64_encode = base64.encodestring(image_read).decode("utf-8")
                print('______________',type(image_64_encode))
            for i in search_user_id:
                IrDefault = odoo.env['ir.default']
                title_request=odoo.env['res.partner.title'].create({'name': request.user.profile.title})
                models.execute_kw(db, uid, odoopassword, 'res.partner', 'write', [[i],
                {'image': image_64_encode,
                 'mobile':request.user.profile.mobile,
                 'street':request.user.profile.street,
                 'street2':request.user.profile.street2,
                 'function':request.user.profile.job,
                 'city': request.user.profile.city,
                 'country_id':int(request.user.profile.country),
                 'title':title_request,}])
            return redirect('eshop:home')

        else:
             messages.error(request, ('Please correct the error below.'))
    else:
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'eshop/edit_profile.html', {
        'profile_form': profile_form })




def login_user(request):
    if request.method == "POST" or 'login' in request.POST:
        username = request.POST.get('username')
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)

                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                return render(request, 'eshop/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'eshop/login.html', {'error_message': 'Invalid login'})
    return render(request, 'eshop/login.html')


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return HttpResponseRedirect(settings.LOGIN_URL)








