import random
import stripe

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import *
from .models import Rate, Ingredient, Recipe, RecipeItem, Order
from environs import Env

env = Env()
stripe.api_key = env('STRIPE_API_KEY')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'registration.html'
    success_url = reverse_lazy('auth')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'auth.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return dict(list(context.items()))

    def get_success_url(self):
        return reverse_lazy('lk')


def logout_user(request):
    logout(request)
    request.session.clear()
    return redirect('index')


def free_recipes(request):
    recipes = []
    try:
        random_breakfast = random.sample(list(Recipe.objects.filter(meal_time='завтрак')), k=1)[0]
        recipes.append(random_breakfast)
    except ValueError:
        pass
    try:
        random_lunch = random.sample(list(Recipe.objects.filter(meal_time='обед')), k=1)[0]
        recipes.append(random_lunch)
    except ValueError:
        pass
    try:
        random_dinner = random.sample(list(Recipe.objects.filter(meal_time='ужин')), k=1)[0]
        recipes.append(random_dinner)
    except ValueError:
        pass
    try:
        random_dessert = random.sample(list(Recipe.objects.filter(meal_time='десерт')), k=1)[0]
        recipes.append(random_dessert)
    except ValueError:
        pass
    return render(request, 'free_recipes.html', {'recipes': recipes})


def index(request):
    # if request.session.get('current_user'):
    #     current_user = request.session.get('current_user')
    #     request.session.clear()
    #     request.session['current_user'] = current_user
    return render(request, 'index.html')


def auth(request):
    return render(request, 'auth.html')


def registration(request):
    return render(request, 'registration.html')


def lk(request):
    request.session['current_user'] = request.user.id
    return render(request, 'lk.html')


def order(request):
    return render(request, 'order.html')


def card(request):
    return render(request, 'card.html')


# тут лучше как то использовать класс Types из модели Recipe
foodtypes = {
        'classic': 'классическое',
        'low_carb': 'низкоуглеводное',
        'vegetarian': 'вегетарианское',
        'keto': 'кето',
    }


def pay(request):
    try:
        user = get_object_or_404(User, pk=request.session['current_user'])
    except KeyError:
        return render(request, 'pay.html', {'warning': 'До оформления заказа необходимо войти или зарегистрироваться'})
    context = {
        'foodtype': foodtypes[request.POST.get('foodtype')],
        'term': int(request.POST.get('term')),
        'breakfasts': bool(int(request.POST.get('breakfasts'))),
        'lunches': bool(int(request.POST.get('lunches'))),
        'dinners': bool(int(request.POST.get('dinners'))),
        'desserts': bool(int(request.POST.get('desserts'))),
        'persons_number': int(request.POST.get('persons_number')),
        'allergy1': bool(request.POST.get('allergy1')),
        'allergy2': bool(request.POST.get('allergy2')),
        'allergy3': bool(request.POST.get('allergy3')),
        'allergy4': bool(request.POST.get('allergy4')),
        'allergy5': bool(request.POST.get('allergy5')),
        'allergy6': bool(request.POST.get('allergy6')),
        'promocode': request.POST.get('promocode'),
    }

    allergies = ''
    for num in range(6):
        if context[f'allergy{num+1}']:
            allergies += f'{num+1}'

    price = 0
    if context['breakfasts']:
        price += 400
    if context['lunches']:
        price += 700
    if context['dinners']:
        price += 500
    if context['desserts']:
        price += 200
    # увеличение за рассчет на количество человек
    price += (100 * context['persons_number'])

    # для промокодов целесообразно создать отдельную модель и рулить ими в админке
    # if context['promocode'] in request.session['promocodes']:
    if context['promocode'] == '12345':
        price *= 0.8

    for num in range(6):
        if context[f'allergy{num+1}']:
            price += 100

    context['price'] = price
    request.session['context'] = context

    # почему-то всегда создает новую запись тарифа, какие то символы преобразуются в процессе создания? может аллергии?
    new_rate, rate_created = Rate.objects.get_or_create(
        type=context['foodtype'],
        term=context['term'],
        breakfasts=context['breakfasts'],
        lunches=context['lunches'],
        dinners=context['dinners'],
        desserts=context['desserts'],
        persons_number=context['persons_number'],
        allergies=list(allergies),
        promo_code=context['promocode'],
        defaults={'price': price},
    )

    new_order = Order.objects.create(
        client=user,
        rate=new_rate,
    )
    request.session['order_pk'] = new_order.id
    return render(request, 'pay.html', context)


def process_payment(request):
    if request.method == 'POST':
        context = request.session.get('context')
        user = get_object_or_404(User, pk=request.session['current_user'])
        payment_success = False
        payment_failed = False
        stripe_error = False
        price = context['price']

        try:
            stripe.Charge.create(
                amount=price * 100,
                currency="usd",
                source="tok_visa",  # Используем тестовый токен
                description="Оплата заказа",
                receipt_email=user.email,
            )
            payment_success = True
        except stripe.error.CardError as error:
            payment_failed = True
        except stripe.error.StripeError as error:
            stripe_error = True

        if payment_success:
            new_order = Order.objects.get(pk=request.session.get('order_pk', 0))
            new_order.payed = True
            new_order.save()

        context['payment_success'] = payment_success
        context['payment_failed'] = payment_failed
        context['stripe_error'] = stripe_error

        return render(request, 'pay.html', context)
