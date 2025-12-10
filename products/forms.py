from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'mc_type', 'mc_rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'mc_type': forms.Select(attrs={'class': 'form-control'}),
            'mc_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }
