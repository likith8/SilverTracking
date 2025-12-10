from django import forms
from .models import SilverGiven, ProductReturn
from customers.models import Customer
from products.models import Product

class SilverGivenForm(forms.ModelForm):
    class Meta:
        model = SilverGiven
        fields = ['customer', 'weight', 'date']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
        }

class ProductReturnForm(forms.ModelForm):
    class Meta:
        model = ProductReturn
        fields = ['customer', 'product', 'gross_weight', 'melting_percent', 'date',"mc_given",
            "mc_given_date"]
        widgets = {
    'customer': forms.Select(attrs={'class': 'form-control'}),
    'product': forms.Select(attrs={'class': 'form-control'}),
    'gross_weight': forms.NumberInput(attrs={'class': 'form-control'}),
    'melting_percent': forms.NumberInput(attrs={'class': 'form-control'}),
    'date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
    'mc_given': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    'mc_given_date': forms.DateInput(attrs={'class': 'form-control', 'type':'date'}),
}

def clean(self):
        cleaned_data = super().clean()
        mc_given = cleaned_data.get("mc_given")
        mc_given_date = cleaned_data.get("mc_given_date")

        if mc_given and not mc_given_date:
            raise forms.ValidationError("Please enter MC Given Date since MC is marked as given.")

        return cleaned_data

