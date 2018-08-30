from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<category_name_url>/', views.category, name='category'),
    path('about/', views.about, name='about'),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<category_name_url>/add_page/', views.add_page, name='add_page'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('goto/', views.track_url, name='track_url'),
    path('like_category/', views.like_category, name="like_category"),
    path('suggest_category/', views.suggest_category, name="suggest_category"),
    path('auto_add_page/', views.auto_add_page, name="auto_add_page"),
]