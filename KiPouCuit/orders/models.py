from django.db import models
from django.contrib.auth.models import User
from meals.models import MenuItem


class OrderItem(models.Model):
    """
    Single line item inside an Order. Status flows:
      pending -> accepted -> delivering -> delivered
    """
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
    """
    An Order that groups many OrderItem rows.

    Important: status is computed from the contained OrderItem objects,
    so we don't keep a redundant status field on the Order itself.
    Use the `status` property to get the overall state.
    """
    items = models.ManyToManyField(OrderItem, related_name="orders")
    client_name = models.CharField(max_length=150, default="Anonymous")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} ({self.client_name})"

    @property
    def subtotal(self):
        """Sum of all item totals."""
        return sum(item.total_price for item in self.items.all())

    @property
    def status(self):
        """
        Compute overall order status from item statuses.
        Priority (highest → lowest):
          - delivered   (all items delivered)
          - delivering  (any item delivering)
          - accepted    (any item accepted)
          - pending     (default)
        Returns one of: "delivered", "delivering", "accepted", "pending"
        """
        # Gather unique statuses among items
        statuses = set(self.items.values_list("status", flat=True))

        # If there are no items, treat as pending
        if not statuses:
            return "pending"

        # If every item is delivered -> delivered
        if statuses == {OrderItem.Status.DELIVERED}:
            return "delivered"

        # If any item is delivering -> delivering
        if OrderItem.Status.DELIVERING in statuses:
            return "delivering"

        # If any item is accepted -> accepted
        if OrderItem.Status.ACCEPTED in statuses:
            return "accepted"

        # Otherwise pending
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
