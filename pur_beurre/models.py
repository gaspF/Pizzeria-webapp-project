from django.contrib.auth.models import User
from django.db import models


class Categories(models.Model):
    name = models.CharField(max_length=500, unique=True)
    product_count = models.IntegerField(default=0)
    url = models.URLField()
    off_id = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name="Nom", max_length=150)
    nutriscore = models.CharField(verbose_name='Nutriscore', max_length=1)
    brand = models.CharField(verbose_name='Marque', max_length=200, blank=True)
    itemcode = models.CharField(verbose_name='Code Produit', max_length=150, blank=True)
    description = models.TextField(verbose_name='Description', blank=True)
    image = models.URLField(blank=True, default="http://www.imagespourtoi.com/image/892.html")
    openfoodfacts_link = models.URLField(verbose_name='URL Openfoodfacts', blank=True)
    categories = models.ManyToManyField('Categories')

    def __str__(self):
        return self.name


class SavedProduct(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['saved_by', 'saved_product'], name='saved_association'),
            ]

    saved_by = models.ForeignKey(User, verbose_name="Sauvegardé par", on_delete=models.CASCADE,)
    saved_product = models.ForeignKey(Product, verbose_name='Produit sauvegardé', on_delete=models.CASCADE,)

    def __str__(self):
        return self.saved_product






