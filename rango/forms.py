from django import forms
from django.contrib.auth.models import User

from .models import Category, Page, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter category name")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # An inline class to provide additional information on the form
    class Meta:
        # provide an association between ModelForm and and a molde
        model = Category

        # allow certain fileds to be displayed
        fields = ('name', 'views', 'likes')

class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Pleaase enter URL of the page")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean(self):
        cleaned_date = self.cleaned_data
        url = cleaned_date.get('url')

        # if url is not empty and doest start with http://, prepend 'http://'
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_date['url'] = url

        return cleaned_date

    class Meta:
        # Provide association between ModelForm and Page model
        model = Page

        # allow certain fileds to be displayed
        fields = ('title', 'url', 'views')


class UserForm(forms.ModelForm):
    username = forms.CharField(help_text="Please enter your username.")
    email = forms.CharField(help_text="Please enter your email.")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Please enter your password.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(help_text="Please enter your website.", required=False)
    picture = forms.ImageField(help_text="Select a profile Image to upload.", required=False)

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
