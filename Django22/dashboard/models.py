from django.db import models

class ProductCategory(models.Model):
    ID_Product = models.CharField(max_length=50, primary_key=True)
    tanggal = models.DateField()
    product_category_name = models.CharField(max_length=255)
    product_name_length = models.IntegerField()
    product_description_length = models.IntegerField()

    def __str__(self):
        return self.product_category_name

class ProductShape(models.Model):
    ID_Shape = models.AutoField(primary_key=True)
    product_length_cm = models.DecimalField(max_digits=6, decimal_places=2)
    product_width_cm = models.DecimalField(max_digits=6, decimal_places=2)
    product_height_cm = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.product_length_cm}x{self.product_width_cm}x{self.product_height_cm}"

class ShippingCost(models.Model):
    ID_Shipping = models.AutoField(primary_key=True)
    Shipping_Cost = models.DecimalField(max_digits=10, decimal_places=2)
    ID_Shape = models.ForeignKey(ProductShape, on_delete=models.CASCADE)
    ID_Product = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    tanggal = models.DateField()

    def __str__(self):
        return f"{self.ID_Product.product_category_name} - {self.Shipping_Cost}"
