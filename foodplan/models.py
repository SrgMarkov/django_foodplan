from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from multiselectfield import MultiSelectField
from django.utils.timezone import now
from django.contrib.auth.models import User


ALLERGIES = (
    (1, 'Рыба и морепродукты'),
    (2, 'Мясо'),
    (3, 'Зерновые'),
    (4, 'Продукты пчеловодства'),
    (5, 'Орехи и бобовые'),
    (6, 'Молочные продукты')
)


class Types(models.TextChoices):
    CLASSIC = 'классическое', 'классическое'
    LOW_CARB = 'низкоуглеводное', 'низкоуглеводное'
    VEGETARIAN = 'вегетарианское', 'вегетарианское'
    KETO = 'кето', 'кето'


class Rate (models.Model):

    type = models.CharField(
        'тип меню',
        choices=Types.choices,
        default=Types.CLASSIC,
        max_length=30
    )

    term = models.IntegerField(
        'срок',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12),
        ])

    breakfasts = models.BooleanField(
        'завтраки',
        default=True,
        db_index=True,
    )

    lunches = models.BooleanField(
        'обеды',
        default=True,
        db_index=True,
    )

    dinners = models.BooleanField(
        'ужины',
        default=True,
        db_index=True,
    )

    desserts = models.BooleanField(
        'десерты',
        default=True,
        db_index=True,
    )

    persons_number = models.IntegerField(
        'количество персон',
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(6),
        ])

    allergies = MultiSelectField(
        'наличие аллергии',
        choices=ALLERGIES,
        max_length=11,
        null=True,
        blank=True,
    )

    promo_code = models.CharField(
        'промокод',
        max_length=50,
        blank=True,
        null=True,
    )

    price = models.IntegerField(
        'цена',
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100000),
        ])

    class Meta:
        verbose_name = 'тариф'
        verbose_name_plural = 'тарифы'

    def __str__(self):
        return f'{self.type} {self.term} {self.breakfasts} {self.lunches} {self.dinners} {self.desserts} ' \
               f'{self.persons_number} {self.price} руб.'


class Ingredient (models.Model):

    name = models.CharField(
        'название',
        max_length=50,
    )

    calories = models.IntegerField(
        'калорий на 100 гр.',
        default=0,
    )

    proteins = models.IntegerField(
        'белков на 100 гр.',
        default=0,
    )

    fats = models.IntegerField(
        'жиров на 100 гр.',
        default=0,
    )

    carbohydrates = models.IntegerField(
        'углеводов на 100 гр.',
        default=0,
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name} {self.calories} ккал'


class Recipe (models.Model):

    name = models.CharField(
        'название',
        blank=True,
        null=True,
        max_length=150,
    )

    image = models.ImageField(
        'фото',
        null=True,
        blank=True,
    )

    class MealTimes(models.TextChoices):
        BREAKFAST = 'завтрак', 'завтрак'
        LUNCH = 'обед', 'обед'
        DINNER = 'ужин', 'ужин'
        DESSERT = 'десерт', 'десерт'

    meal_time = models.CharField(
        'время приема пищи',
        choices=MealTimes.choices,
        max_length=10
    )

    type = models.CharField(
        'тип меню',
        choices=Types.choices,
        default=Types.CLASSIC,
        max_length=30
    )

    allergies = MultiSelectField(
        'противопоказания (аллергии)',
        choices=ALLERGIES,
        max_length=11,
        null=True,
        blank=True,
    )

    calories = models.IntegerField(
        'калорий',
        default=0,
    )

    description = models.TextField(
        'описание',
        null=True,
        blank=True,
        max_length=1500,
    )

    relevance = models.BooleanField(
        'актуальность',
        default=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return f'{self.name} {self.calories} ккал'


class RecipeItem (models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_items',
        verbose_name='рецепт',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_items',
        verbose_name='ингредиент',
    )

    weight = models.IntegerField(
        'вес',
        db_index=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(1000),
        ],
    )


class Order(models.Model):
    client = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name='клиент',
    )

    rate = models.ForeignKey(
        Rate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name='тариф',
    )

    created_datetime = models.DateTimeField(
        'дата и время заказа',
        default=now,
        editable=False,
    )

    comment = models.TextField(
        'Комментарий к заказу',
        blank=True,
    )

    payed = models.BooleanField(
        'Оплачен?',
        default=False
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.pk} {self.rate.__str__}'
