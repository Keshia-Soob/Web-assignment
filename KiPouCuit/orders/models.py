from django.db import models
from django.contrib.auth.models import User
from meals.models import MenuItem


class OrderItem(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"          
        ACCEPTED = "accepted", "Accepted"        
        DELIVERING = "delivering", "Being delivered"
        DELIVERED = "delivered", "Delivered"     

    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    prepared_by = models.ForeignKey(
        "homecook.HomeCook",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="prepared_items"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.menu_item.name} (x{self.quantity}) - {self.status}"

    @property
    def total_price(self):
        return self.menu_item.price * self.quantity


class Order(models.Model):

    items = models.ManyToManyField(OrderItem, related_name="orders")
    client_name = models.CharField(max_length=150, default="Anonymous")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.client_name})"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def status(self):

 
        statuses = set(self.items.values_list("status", flat=True))

        if not statuses:
            return "pending"
        
        if statuses == {OrderItem.Status.DELIVERED}:
            return "delivered"

        if OrderItem.Status.DELIVERING in statuses:
            return "delivering"

        if OrderItem.Status.ACCEPTED in statuses:
            return "accepted"

        return "pending"

    def is_fully_delivered(self) -> bool:
        """Return True when all items are delivered."""
        return self.status == "delivered"

    @property
    def human_readable_status(self) -> str:
        """Friendly text for templates (you can expand localisation later)."""
        mapping = {
            "pending": "Pending (kitchen)",
            "accepted": "Accepted by cook",
            "delivering": "Is being delivered",
            "delivered": "Delivered",
        }
        return mapping.get(self.status, self.status)
