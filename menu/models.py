from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Menu section: starters, main courses, desserts, drinks, etc."""

    name = models.CharField('Name', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=120, unique=True, blank=True)
    position = models.PositiveSmallIntegerField('Position', default=0)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['position', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Allergen(models.Model):
    """Allergen: gluten, nuts, lactose, etc."""

    name = models.CharField('Name', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Allergen'
        verbose_name_plural = 'Allergens'
        ordering = ['name']

    def __str__(self):
        return self.name


class Dish(models.Model):
    """A dish or a drink."""

    category = models.ForeignKey(
        Category,
        verbose_name='Category',
        on_delete=models.PROTECT,
        related_name='dishes',
    )
    name = models.CharField('Name', max_length=150)
    slug = models.SlugField('Slug', max_length=170, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    price = models.DecimalField(
        'Price',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    image = models.ImageField('Image', upload_to='dishes/', blank=True)
    weight_grams = models.PositiveIntegerField('Weight / volume (g or ml)', null=True, blank=True)
    calories = models.PositiveIntegerField('Calories (kcal)', null=True, blank=True)
    allergens = models.ManyToManyField(
        Allergen,
        verbose_name='Allergens',
        blank=True,
        related_name='dishes',
    )
    is_vegetarian = models.BooleanField('Vegetarian', default=False)
    is_spicy = models.BooleanField('Spicy', default=False)
    is_featured = models.BooleanField('Featured', default=False)
    is_available = models.BooleanField('Available now', default=True)
    created_at = models.DateTimeField('Created at', auto_now_add=True)
    updated_at = models.DateTimeField('Updated at', auto_now=True)

    class Meta:
        verbose_name = 'Dish'
        verbose_name_plural = 'Dishes'
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} - {self.price}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)