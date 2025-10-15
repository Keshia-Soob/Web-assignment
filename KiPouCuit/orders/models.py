from django.db import models
from meals.models import MenuItem

class OrderItem(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.menu_item.name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.menu_item.price * self.quantity


class Order(models.Model):
    items = models.ManyToManyField(OrderItem)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id}"