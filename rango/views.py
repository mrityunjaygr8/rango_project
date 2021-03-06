from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render,redirect
from rango.models import Category, Page
from rango.forms import CategoryForm,PageForm,UserForm,UserProfileForm
from django.contrib.auth.decorators import login_required
from rango.bing_search import run


def index(request):
    category_list = Category.objects.order_by("-likes")[:5]

    pages=Page.objects.order_by("-views")[:5]
    context_dict = {'categories': category_list,'pages':pages}

    visits=request.session.get('visits')

    if not visits:
        visits=1
    reset_last_visit_time=False

    last_visit=request.session.get('last_visit')

    if last_visit:
        last_visit_time=datetime.strptime(last_visit[:-7],"%Y-%m-%d %H:%M:%S")

        if (datetime.now()-last_visit_time).seconds>0:
            visits+=1
            reset_last_visit_time=True
    else:
        reset_last_visit_time=True

    if reset_last_visit_time:
        request.session['last_visit']=str(datetime.now())
        request.session['visits']=visits
    context_dict['visits']=visits

    return render(request,'rango/index.html',context_dict)


def about(request):
    visits = request.session.get('visits')
    context_dict = {'boldmessage': "Me......",'visits':visits}
    return render(request, 'rango/about.html', context_dict)


def category(request, category_name_slug):
    context_dict = {}
    context_dict['result_list']=None
    context_dict['query']=None

    if request.method=='POST':
        query=request.POST['query'].strip()

        if query:
            result_list=run(query)

            context_dict['result_list']=result_list
            context_dict['query']=query


    try:
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages

        context_dict['category'] = category
        context_dict['category_name_slug']=category_name_slug


    except Category.DoesNotExist:
        pass

    if not context_dict['query']:
        context_dict['query']=category.name

    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    if request.method=='POST':
        form=CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)

        else:
            print form.errors
    else:
        form=CategoryForm()

    return render(request,'rango/add_category.html',{'form':form})
@login_required
def add_page(request,category_name_slug):

    try:
        cat=Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat=None

    if request.method=='POST' :
        form=PageForm(request.POST)
        if form.is_valid():
            if cat:
                page=form.save(commit=False)
                page.category=cat
                page.views=0
                page.save()

                return category(request,category_name_slug)
        else:
            print form.errors
    else:
        form=PageForm()

    context_dict={'form':form,'category':cat}

    return render(request,'rango/add_page.html',context_dict)

def register(request):
    registered=False
    if request.method=="POST":
        user_form=UserForm(data=request.POST)
        profile_form=UserProfileForm(data=request.POST)


        if user_form.is_valid() and profile_form.is_valid():
            user=user_form.save()
            user.set_password(user.password)
            user.save()

            profile=profile_form.save(commit=False)
            profile.user=user

            if 'picture' in request.FILES:
                profile.picture=request.FILES['picture']

            profile.save()

            registered=True

        else:
            print user_form.errors,profile_form.errors

    else:
        user_form=UserForm()
        profile_form=UserProfileForm()

    return render(request,'rango/register.html',{'user_form':user_form,'profile_form':profile_form,'registered':registered})

def user_login(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your rango account is diabled')

        else:
            print "invalid login details :{0},{1}".format(username,password)
            return HttpResponse("Invalid Login details supplied")
    else:
        return render(request,'rango/login.html',{})

@login_required
def restricted(request):
    return HttpResponse("as you are logged in,you can see this")

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')

# def search(request):
#     results_list=[]
#     if request.method=="POST":
#         query=request.POST['query'].strip()

#         if query:
#             results_list=run(query)

#     return render(request,'rango/search.html',{"result_list":results_list})

def goto(request):
    if request.method=="GET":
        if 'page_id' in request.GET:
            page_id=request.GET['page_id']

def track_url(request):
    page_id=None
    url='/rango/'
    if request.method=="GET":
        if 'page_id' in request.GET:
            page_id=request.GET['page_id']
            try:
                page=Page.objects.get(id=page_id)
                page.views=page.views+1
                page.save()
                url=page.url
            except:
                pass
    return redirect(url)