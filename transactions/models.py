from django.db import models
from customers.models import Customer
from products.models import Product

class SilverGiven(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    weight = models.FloatField()  # shop gives silver
    date = models.DateField()

    def __str__(self):
        return f"Silver Given {self.weight} g to {self.customer}"

class ProductReturn(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    gross_weight = models.FloatField()
    melting_percent = models.FloatField()
    pure_weight = models.FloatField()
    mc_amount = models.DecimalField(max_digits=10, decimal_places=3)
    date = models.DateField()
    mc_given = models.BooleanField(default=False)
    mc_given_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Product Return {self.customer}"
