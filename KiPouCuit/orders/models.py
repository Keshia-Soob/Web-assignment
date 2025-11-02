from django.db import models
from meals.models import MenuItem

class OrderItem(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready"

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    # NEW FIELDS for homecook integration
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    prepared_by = models.ForeignKey(
        "homecook.HomeCook", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="prepared_items"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.menu_item.name} (x{self.quantity}) - {self.status}"

    @property
    def total_price(self):
        return self.menu_item.price * self.quantity


class Order(models.Model):
    items = models.ManyToManyField(OrderItem, related_name="orders")
    client_name = models.CharField(max_length=150, default="Anonymous")  # NEW for display in log
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} ({self.client_name})"