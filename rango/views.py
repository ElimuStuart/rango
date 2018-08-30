from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import Category, Page, UserProfile
from .forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query
from django.contrib.auth.models import User


# encode function
def encode_url(str):
    return str.replace(' ', '_')

# decode function
def decode_url(str):
    return str.replace('_', ' ')

# index view.
def index(request):
    # request.session.set_test_cookie()
    category_list = Category.objects.order_by('-likes')[:5]
    # load the template
    page_list = Page.objects.order_by('-views')[:5]

    cat_list = get_category_list()

    template = loader.get_template('rango/index.html')
    # dictionary with variables
    context = {
        'categories': category_list,
        'pages': page_list,
        'cat_list': cat_list,
    }

    for category in category_list:
        category.url = category.name.replace(' ', '_')


    if request.session.get('last_visit'):
        # the session has a value for the last visit
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        # get returns none and session has no value for last visit
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1
    return HttpResponse(template.render(context, request))


# category view


def category(request, category_name_url):
    template = loader.get_template('rango/category.html')
    # replace underscores with spaces in category name
    category_name = decode_url(category_name_url)

    cat_list = get_category_list()

    context = {
        'category_name': category_name,
        'category_name_url': category_name_url,
        'cat_list': cat_list,
    }

    try:
        # find category with given name
        category = Category.objects.get(name=category_name)

        # find pages associated with category
        pages = Page.objects.filter(category=category)

        # add result to context
        context['pages'] = pages

        # also add category object from database
        context['category'] = category

    except Category.DoesNotExist:
        pass

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)
            context['result_list'] = result_list

    return HttpResponse(template.render(context, request))
    

# about view
def about(request):
    # if the visits session variable exists, take it and use it
    # if it doesn't we haven't visited the site, set to zero

    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    template = loader.get_template('rango/about.html')
    context = {
        'somemessage': "*us",
        'visits': count
    }

    return HttpResponse(template.render(context, request))


# like a category view
@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes  = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)

# add category view
def add_category(request):
    template = loader.get_template('rango/add_category.html')
    # A HTTP POST
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # is the form valid
        if form.is_valid():
            form.save(commit=True)
            # call index view
            return index(request)
        else:
            print(form.errors)
    else:
        form = CategoryForm()

    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))

# get categories view
def get_category_list():
    cat_list = Category.objects.all()

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list


# track url
def track_url(request):
    page_id = None
    url = '/rango'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)


# add page to category
def add_page(request, category_name_url):
    template = loader.get_template('rango/add_page.html')
    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)

            # retrieve associated category objects
            cat = Category.objects.get(name = category_name_url)
            page.category = cat

            # default value for number of views
            page.views = 0

            # can now save
            page.save()

            return category(request, category_name_url)
        else:
            print(form.errors)
    else:
        form = PageForm()

    context = {
        'category_name_url': category_name_url,
        'category_name': category_name,
        'form': form,
    }

    return HttpResponse(template.render(context, request))


# get categories
def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)
    else:
        cat_list = Category.objects.all()

    if max_results > 0:
        if len(cat_list) > max_results:
            cat_list = cat_list[:max_results]

    for cat in cat_list:
        cat.url = encode_url(cat.name)

    return cat_list


# suggest category view
def suggest_category(request):
    cat_list = []
    starts_with = ''
    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    else:
        starts_with = request.POST['suggestion']

        cat_list = get_category_list(8, starts_with)

    template = loader.get_template('rango/category_list.html')
    context = {
        'cat_list': cat_list,
    }
    return HttpResponse(template.render(context, request))


# add result page to category
@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)

            pages = Page.objects.filter(category=category).order_by('-views')
            context['pages'] = pages

    template = loader.get_template('rango/page_list.html')
    return HttpResponse(template.render(context, request))


# registration
def register(request):
    # testing cookies
    # if request.session.test_cookie_worked():
    #     print(">>> TEST COOKIE WORKED")
    #     request.session.delete_test_cookie()

    # boolean to tell template if registration was successful
    # set to false initially, will change when registration is successful
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # if the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # save user's form data to database
            user = user_form.save()

            # hash the password
            user.set_password(user.password)
            user.save()

            # userprofile instance
            # since we need to set user attribute ourselves we set commit to False
            profile = profile_form.save(commit=False)
            profile.user = user

            # did user provide profile picture?
            # if yes get from the input form and put it in UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

                # save userprofile instance
                profile.save()

                # update registered
                registered = True

        # invalid form or errors
        else:
            print(user_form.errors, profile_form.errors)

    # not an HTTP post, forms remain blank
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # get the template
    template = loader.get_template('rango/register.html')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered,
    }

    return HttpResponse(template.render(context, request))


# log in
def user_login(request):
    # if request is a post, try to pull out relevant details
    template = loader.get_template('rango/login.html')


    if request.method == 'POST':
        # gather username and password
        # this information is obtained from login form
        username = request.POST['username']
        password = request.POST['password']

        # check if valid
        user = authenticate(username=username, password=password)

        # if valid
        if user is not None:
            # if account is active
            if user.is_active:
                # if account is active and valid
                # log in user and send to home page
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                # inactive account, no log in
                return HttpResponse("Your Rango account was disabled")
        else:
            # wrong details, no login
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied")
    else:
        # request not a post
        context = {

        }
        return HttpResponse(template.render(context, request))

# restricting users
@login_required
def restricted(request):

    template = loader.get_template('rango/restricted.html')

    context = {

    }
    return HttpResponse(template.render(context, request))

# logout function
@login_required
def user_logout(request):
    # logout user
    logout(request)

    # take user back to homepage
    return HttpResponseRedirect('/rango/')

# bing search
def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    context = {
        'result_list': result_list
    }
    template = loader.get_template('rango/search.html')
    return HttpResponse(template.render(context, request))

@login_required
def profile(request):
    cat_list = get_category_list()
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context = {
        'cat_list': cat_list,
        'user':  u,
        'userprofile': up,
    }

    template = loader.get_template('rango/profile.html')
    return HttpResponse(template.render(context, request))
