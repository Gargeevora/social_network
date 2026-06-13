from django import forms
from .models import Book


class SellBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'book_name',
            'publisher_name',
            'edition_year',
            'condition',
            'price',
            'description',
            'book_photo',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_edition_year(self):
        year = self.cleaned_data.get('edition_year')
        if year < 1900 or year > 2026:
            raise forms.ValidationError('Enter a valid edition year.')
        return year

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        return price

    def clean_book_photo(self):
        photo = self.cleaned_data.get('book_photo')
        if not photo and not self.instance.book_photo:
            raise forms.ValidationError('Please upload a photo of the book.')
        return photo


class PurchaseRequestForm(forms.Form):
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Message to Seller (optional)',
        help_text='You can add a message for the seller.'
    )