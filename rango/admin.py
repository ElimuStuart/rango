from django.contrib import admin
from .models import Category, Page, UserProfile


# customise admin interface
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')


# Register your models here.
admin.site.register(Category)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)

