from django.db import models

class PackagingData(models.Model):
    tanggal = models.DateField()
    recommended_packaging = models.CharField(max_length=50)
