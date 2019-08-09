import time

from django.http import JsonResponse
from path import Path

import stripe
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from mysite import settings
from mysite.core.models import Profile, Item, Vendor
import pickle
from mysite.forms import UserForm, ProfileForm, SaleForm

stripe.api_key = settings.STRIPE_SECRET_KEY  # new


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


# ------------------------------------------------------------------------------------------
def home(request):
    # home page: show only when user is logged in, otherwise go to sigin page
    if request.user.is_authenticated:
        count = User.objects.count()
        return render(request, 'home.html', {
            'count': count
        })
    else:
        return redirect('login')


# ------------------------------------------------------------------------------------------
def signup(request):
    # after login, user is redirected to signup to check if all information for user is registered,
    # first time user registers and logs in, specially after logging in with OAuth, he has to fill
    # in registration form in "signup" page.
    # There is will be a bit (user_is_registered) in registration Model which will be set when user registers all information
    #
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })


# ------------------------------------------------------------------------------------------
@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            profile_ = Profile.objects.get(user=request.user)
            profile_.profile_filled = True
            profile_.save()
            return redirect('home')
        else:
            return redirect('update_profile')
    else:
        profile_ = Profile.objects.get(user=request.user)
        if profile_.profile_filled:
            return redirect('home')
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# ------------------------------------------------------------------------------------------
def update_profile_after_initial(request):
    profile_ = Profile.objects.get(user=request.user)
    profile_.profile_filled = False
    profile_.save()
    return redirect('update_profile')


# ------------------------------------------------------------------------------------------
def register(request):
    return redirect(update_profile_after_initial())


# ------------------------------------------------------------------------------------------
@login_required
def signup_additional(request):
    return render(request, 'registration/signup_additional.html')


# ------------------------------------------------------------------------------------------
@login_required
def cart_page(request):
    with open(request.session.session_key + '.pickle', 'rb') as handle:
        unserialized_data = pickle.load(handle)
    temp_order = unserialized_data
    print(temp_order)
    # items = Item.objects.all()
    return render(request, 'cart.html', {
        # 'Items': items,
        'Number_of_items': temp_order,
    })


# Second way to create secret page
# class SecretPage(LoginRequiredMixin, TemplateView):
#    template_name = 'secret_page.html'


# deletes .pickle files older than one day
def delete_files():
    d = Path("mysite/..")
    for i in d.walk():
        if i.endswith(".pickle"):
            DAYS = 1
            time_in_secs = time.time() - (DAYS * 24 * 60 * 60)
            if i.isfile():
                if i.mtime <= time_in_secs:
                    i.remove()


# ------------------------------------------------------------------------------------------
@login_required
def order_page(request):
    delete_files()
    if request.method == 'POST':
        # Store data (serialize)
        with open(request.session.session_key + '.pickle', 'wb') as handle:
            pickle.dump(request.POST, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return redirect('cart')
    else:
        temp_order = ""
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            unserialized_data = pickle.load(handle)
        temp_order = unserialized_data
    except:
        temp_order = ""
    # This has to be searched based on distance
    # have to use vendor = Vendor.objects.filter(profile__user__username="msohani")
    # Then we can use this vendor to filter all the items this Vendor can sell
    vendor = Vendor.objects.get(profile__user__username="msohani")
    items = vendor.item.all()
    # ----------------------------------------
    # create a range of digits 0:20 in string format
    range_ = []
    for _ in range(0, 20):
        range_.append(str(_))
    # ----------------------------------------
    return render(request, 'order.html', {
        'Items': items,
        'Number_of_items': temp_order,
        'range': range_,
    })


# ------------------------------------------------------------------------------------------
def checkout(request):
    pass


# ------------------------------------------------------------------------------------------
class pay(TemplateView):
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):  # new
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


# ------------------------------------------------------------------------------------------
def charged(request):  # new
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=500,
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        return render(request, 'charged.html')


def ajax_test(request):
    print(request.GET)
    data = {
        'data': request.GET["data"]
    }
    return JsonResponse(data)
