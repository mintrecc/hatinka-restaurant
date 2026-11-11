from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Table(models.Model):
    """A table in the restaurant hall."""

    number = models.PositiveSmallIntegerField('Number', unique=True)
    seats = models.PositiveSmallIntegerField('Seats')
    is_active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['number']

    def __str__(self):
        return f'Table #{self.number} ({self.seats} seats)'


class Reservation(models.Model):
    """Table reservation."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservations',
    )
    table = models.ForeignKey(
        Table,
        verbose_name='Table',
        on_delete=models.PROTECT,
        related_name='reservations',
    )
    name = models.CharField('Guest name', max_length=100)
    phone = models.CharField('Phone', max_length=20)
    date = models.DateField('Date')
    time = models.TimeField('Time')
    guests = models.PositiveSmallIntegerField('Number of guests', validators=[MinValueValidator(1)])
    comment = models.TextField('Comment', blank=True)
    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    class Meta:
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'
        ordering = ['-date', '-time']
        constraints = [
            models.UniqueConstraint(
                fields=['table', 'date', 'time'],
                condition=~Q(status='cancelled'),
                name='unique_active_reservation_per_slot',
            ),
        ]

    def __str__(self):
        return f'Reservation for {self.name}: {self.date} {self.time}, {self.table}'


class Order(models.Model):
    """An order: delivery, pickup or dine-in."""

    class OrderType(models.TextChoices):
        DELIVERY = 'delivery', 'Delivery'
        PICKUP = 'pickup', 'Pickup'
        DINE_IN = 'dine_in', 'Dine-in'

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        COOKING = 'cooking', 'Cooking'
        READY = 'ready', 'Ready'
        DELIVERING = 'delivering', 'Out for delivery'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    name = models.CharField('Name', max_length=100)
    phone = models.CharField('Phone', max_length=20)
    order_type = models.CharField('Order type', max_length=20, choices=OrderType.choices, default=OrderType.DELIVERY)
    address = models.CharField('Delivery address', max_length=255, blank=True)
    table = models.ForeignKey(
        Table,
        verbose_name='Table',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    comment = models.TextField('Comment', blank=True)
    status = models.CharField('Status', max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} by {self.name}'

    @property
    def total(self):
        return sum((item.subtotal for item in self.items.all()), Decimal('0'))


class OrderItem(models.Model):
    """An order line. The price is frozen at the moment of ordering."""

    order = models.ForeignKey(
        Order,
        verbose_name='Order',
        on_delete=models.CASCADE,
        related_name='items',
    )
    dish = models.ForeignKey(
        'menu.Dish',
        verbose_name='Dish',
        on_delete=models.PROTECT,
        related_name='order_items',
    )
    quantity = models.PositiveSmallIntegerField('Quantity', default=1, validators=[MinValueValidator(1)])
    price = models.DecimalField('Unit price', max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'

    def __str__(self):
        return f'{self.dish.name} x {self.quantity}'

    @property
    def subtotal(self):
        return self.price * self.quantity

    def save(self, *args, **kwargs):
        if self.price is None:
            self.price = self.dish.price
        super().save(*args, **kwargs)