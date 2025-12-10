from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    
    MC_CHOICES = [
        ('per_gram', 'MC per Gram'),
        ('per_kg', 'MC per KG'),
    ]

    mc_type = models.CharField(
        max_length=20,
        choices=MC_CHOICES,
        default='per_kg'
    )
    
    mc_rate = models.FloatField()   # rate per gram or per kg based on choice

    def __str__(self):
        return self.name
