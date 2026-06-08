from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['caption', 'image']
        widgets = {
            'caption': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write a caption...'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        caption = cleaned_data.get('caption')
        image = cleaned_data.get('image')
        if not caption and not image:
            raise forms.ValidationError('Post must have either a caption or an image.')
        return cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 1,
                'placeholder': 'Write a comment...'
            }),
        }