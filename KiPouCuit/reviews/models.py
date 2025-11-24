from django.db import models

# Create your models here.

class Review(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    # phone = models.CharField(max_length=15, blank=True, null=True)
    rating = models.IntegerField(choices=[(i, f"{i} Star") for i in range(1, 6)])
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.rating} Stars"