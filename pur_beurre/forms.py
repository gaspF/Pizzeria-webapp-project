from django import forms
from .models import Categories


class CategoriesForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ('name', 'product_count', 'url', 'off_id')


class FoodRequestForm(forms.Form):
    food = forms.CharField(max_length=500,
                           widget=forms.TextInput(
                               attrs={'class': 'form-control',
                                      'placeholder': 'Entrez votre produit ici',
                                      'aria-label': 'Produit',
                                      'required': 'True'}
                           ))
