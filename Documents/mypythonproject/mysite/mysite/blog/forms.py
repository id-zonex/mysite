from django import forms
from .models import *


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class SavedForm(forms.ModelForm):
    class Meta:
        model = SavedPosts
        fields = ('post',)
