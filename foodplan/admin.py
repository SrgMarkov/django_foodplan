from django.contrib import admin
from django.utils.html import format_html
from .models import Rate, Ingredient, Recipe, RecipeItem, Order
from rangefilter.filters import NumericRangeFilterBuilder


def update_calories(recipe):
    if recipe.recipe_items:
        recipe_items = recipe.recipe_items
        recipe_calories = 0
        for recipe_item in recipe_items.values():
            recipe_calories += Ingredient.objects.filter(pk=recipe_item["ingredient_id"])[0].calories * \
                               recipe_item["weight"] / 100
        recipe.calories = recipe_calories
        recipe.save()


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'admin_image',
        'meal_time',
        'type',
        'allergies',
        'calories',
        'relevance',
    )

    list_filter = [
        'meal_time',
        'type',
        'relevance',
    ]

    search_fields = [
        'name',
        'type',
    ]

    inlines = [
        RecipeItemInline
    ]

    def admin_image(self, obj):
        if obj.image:
            return format_html(
                f'''<a href="{obj.image.url}" target="_blank">
                  <img src="{obj.image.url}" alt="{obj.image}" 
                    width="50" height="50" style="object-fit: cover;"/></a>
                ''')
    admin_image.allow_tags = True

    def save_model(self, request, obj, form, change):
        if obj.pk:
            update_calories(obj)
        super().save_model(request, obj, form, change)

    # def save_formset(self, request, form, formset, change):
    #     instances = formset.save(commit=False)
    #     try:
    #         recipe = instances[0].recipe
    #         for instance in instances:
    #             instance.save()
    #         formset.save_m2m()
    #         update_calories(recipe)
    #     except IndexError:
    #         pass


@admin.register(Rate)
class Rate(admin.ModelAdmin):
    readonly_fields = (
        'price',
    )

    list_display = (
        'type',
        'term',
        'breakfasts',
        'lunches',
        'dinners',
        'desserts',
        'persons_number',
        'allergies',
        'promo_code',
        'price',
    )

    list_filter = [
        'allergies',
        ('persons_number', NumericRangeFilterBuilder()),
    ]

    search_fields = [
        'category',
        'name',
    ]


class RateInline(admin.TabularInline):
    model = Rate
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = (
        'created_datetime',
    )

    list_display = (
        'client',
        'rate',
        'created_datetime',
        'payed',
    )

    search_fields = [
        'rate',
    ]

    list_filter = [
        'payed',
    ]


admin.site.register(Ingredient)

admin.site.site_header = 'Панель управляющего'
admin.site.site_title = '"FoodPlan"'
admin.site.index_title = 'Доступные разделы:'
