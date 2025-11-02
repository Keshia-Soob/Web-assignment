from django.db import models
class MenuItem(models.Model):
    CUISINE_CHOICES = [
        ("indian", "Indian"),
        ("mauritian", "Mauritian"),
        ("english", "English"),
        ("french", "French"),
        ("asian", "Asian"),
    ]

    name        = models.CharField(max_length=120)
    price       = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    cuisine     = models.CharField(max_length=20, choices=CUISINE_CHOICES)
    image       = models.ImageField(upload_to="menu_images/", blank=True, null=True)
    image_url   = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def display_image_url(self) -> str:
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?ixlib=rb-4.0.3"

