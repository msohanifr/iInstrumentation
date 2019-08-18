import time
import json
import pickle
from django.conf.urls import url
from django.contrib.auth import login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from path import Path

import stripe
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from mysite import settings
from mysite.core.models import Profile, Vendor

from twilio.rest import Client
from mysite.core.tokens import account_activation_token, sms_activation_token
from mysite.forms import UserForm, ProfileForm, SignUpForm
from django.contrib.auth.decorators import user_passes_test

stripe.api_key = settings.STRIPE_SECRET_KEY  # new


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def handler403(request):
    return render(request, '403.html', status=403)


# --------------------------------  USER_PASSES_TEST FUNCTION DEFINITIONS -------------------------------
# Create your views here.
# This is just an example for userpass test
# #@user_passes_test(is_mohi, login_url='/home/', redirect_field_name='HOME_REDIRECT_URL')
def is_user_email_verified(user):
    profile = Profile.objects.get(user__username=user)
    print('is_user_email_verified:', user, profile.user_email_verification == 2)
    return profile.user_email_verification == 2


def is_user_phone_verified(user):
    profile = Profile.objects.get(user__username=user)
    return profile.phone_verification_status == 2


# --------------------------------- END_USER_PASSES_TEST ------------------------------------------------

# ----------------   Chronological login process   -----------------------------------------
# ------------------------------------------------------------------------------------------
def signup(request):
    # after login, user is redirected to signup to check if all information for user is registered, first time user
    # registers and logs in, specially after logging in with OAuth, he has to fill in registration form in "signup"
    # page. There is will be a bit (user_is_registered) in registration Model which will be set when user registers
    # all information
    # partially taken from : https://frfahim.github.io/post/django-registration-with-confirmation-email/
    # and from https://simpleisbetterthancomplex.com/tutorial/2016/06/27/how-to-use-djangos-built-in-login-system.html
    if request.method == 'POST':
        print('sigup', request.user)
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # user.is_active = False
            user.save()
            profile = Profile.objects.get(user__username=user.username)
            profile.user_email_verification = 0  # means email verification has started
            profile.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,  ## have to change this
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]

            )
            email.send()
            # return HttpResponse('Please confirm your email address to complete the registration')
            return render(request, 'confirm_email.html')
            # return redirect('home')
    else:
        print('we are in here')
        form = SignUpForm
    return render(request, 'registration/signup.html', {
        'form': form
    })


# -------------------------------------- Send SMS ------------------------------------------------
"""
def sms_response(request):
    print('sms_response:', request.user)
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    account_sid = 'AC8a77fcba5f491b28d836d503873525a4'
    auth_token = 'ed2108cb7b1f056cc6c2a3ff29fed267'
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body="Your code is: " + account_sid,
        from_='+18622608689',
        to='870-814-6955'
    )
    return HttpResponse(message.status)
"""


def send_sms(request):
    # Your Account Sid and Auth Token from twilio.com/console
    # DANGER! This is insecure. See http://twil.io/secure
    print('send_sms:', request.user)
    profile = Profile.objects.get(user__username=request.user)
    user = User.objects.get(username=request.user)
    # user.is_active = False
    # user.save()
    to_phone = profile.phone_number
    account_sid = 'AC8a77fcba5f491b28d836d503873525a4'
    auth_token = 'ed2108cb7b1f056cc6c2a3ff29fed267'
    client = Client(account_sid, auth_token)
    current_site = get_current_site(request)
    message = {
        'user': user,
        'domain': current_site.domain,  ## have to change this
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': sms_activation_token.make_token(user),
    }
    print(message)
    SMS_MSG = "http://" + message['domain'] + '/phone_activate/' + message['uid'] + "/" + message['token']
    client.messages \
        .create(
        body=SMS_MSG,
        from_='+18622608689',
        to=to_phone
    )
    return render(request, 'smssent.html')


def sms_sent(request):
    return render(request, 'smssent.html')


def phone_activate(request, uidb64, token):
    print('in phone activate', request.user)
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        print(user)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and sms_activation_token.check_token(user, token):
        print('phone_activate__if')
        profile_ = Profile.objects.get(user__username=user)
        print(profile_.phone_number)
        profile_.phone_verification_status = 2
        profile_.save()
        # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        logout(request)
        # return redirect('home')
        return HttpResponse('Thank you for your phone confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid! You can request another message by logging in')

# --------------------------------------- End Send SMS -----------------------------------------


# --------------------------------------- Send Email Activation --------------------------------
def resend_email_confirmation(request):
    """
    Sends email confirmation per user request in case user has not received confirmation email yet
    :param request:
    :return: renders the confirmation for email page
    """
    print('resend_email_confirmation:', request.user)
    user = User.objects.get(username=request.user)
    # user.is_active = False
    # user.save()
    to_email = user.email
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,  ## have to change this
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
    })
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.send()
    return render(request, 'confirm_email.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        profile_ = Profile.objects.get(user__username=user.username)
        profile_.user_email_verification = 2
        profile_.save()
        # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        logout(request)
        # return redirect('home')
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
    else:
        return HttpResponse('Activation link is invalid! You can send another request by clicking "Forgot Password" '
                            'at login page.')


# ------------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_user_email_verified, login_url='/resendemailconfirmation/')  # This should be a page that asks
@user_passes_test(is_user_phone_verified, login_url='/sms/')
def home(request):
    # home page: show only when user is logged in, otherwise go to sigin page
    if request.user.is_authenticated:
        profile = Profile.objects.get(user__username=request.user.username)
        print(profile.phone_number)
        count = User.objects.count()
        return render(request, 'home.html', {
            'count': count,
        })
    else:
        return redirect('login')


# ------------------------------------------------------------------------------------------
@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form_data = user_form.cleaned_data
            profile_form_data = profile_form.cleaned_data
            profile_ = Profile.objects.get(user=request.user)
            profile_.profile_filled = True
            user_ = User.objects.get(username=request.user)
            if user_.email != user_form_data['email']:
                profile_.user_email_verification = 0
                # Here we have to set a bit in User model that shows we have to confirm user's email
            if profile_.phone_number != profile_form_data['phone_number']:
                profile_.phone_verification_status = 0
            user_form.save()
            profile_form.save()
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
@user_passes_test(is_user_email_verified, redirect_field_name='/resendemailconfirmation/')
@user_passes_test(is_user_phone_verified, redirect_field_name='/sms/')
def update_profile_after_initial(request):
    profile_ = Profile.objects.get(user=request.user)
    profile_.profile_filled = False
    profile_.save()
    return redirect('update_profile')


# ------------------------------------------------------------------------------------------
def register(request):
    return redirect(update_profile_after_initial)


# ------------------------------------------------------------------------------------------
@login_required
def signup_additional(request):
    return render(request, 'registration/signup_additional.html')


# Second way to create secret page
# class SecretPage(LoginRequiredMixin, TemplateView):
#    template_name = '*.html'


# deletes .pickle files older than one day
def delete_files():
    d = Path("mysite/..")
    for i in d.walk():
        if i.endswith(".pickle"):
            days = 1
            time_in_secs = time.time() - (days * 24 * 60 * 60)
            if i.isfile():
                if i.mtime <= time_in_secs:
                    i.remove()


# ------------------------------------------------------------------------------------------
# Only GET method. The submit button only refers to "CART" page.
# the rest of this function takes care of finding vendor and associated profile
@login_required
def order_page(request):
    delete_files()
    '''
     if request.method == 'POST':
        # Store data (serialize)
        with open(request.session.session_key + '.pickle', 'wb') as handle:
            pickle.dump(request.POST, handle, protocol=pickle.HIGHEST_PROTOCOL)
        return redirect('cart')
    else:
        temp_order = ""
    '''
    # This has to be searched based on distance
    # have to use vendor = Vendor.objects.filter(profile__user__username="msohani")
    # Then we can use this vendor to filter all the items this Vendor can sell
    vendor = Vendor.objects.get(profile__user__username="msohani")
    items_from_vendor = vendor.item.all()
    print('items_from_vendor: ', items_from_vendor)
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            unserialized_data = pickle.load(handle)
        temp_order = unserialized_data
    except:
        temp_order = {}
    print('temp_oredr: ', temp_order)
    items = {}
    # ----------------------------------------
    # create a range of digits 0:20 in string format
    range_ = []
    for _ in range(0, 20):
        range_.append(str(_))
    for _ in items_from_vendor:
        items.update({
            _.title: {
                'title': _.title,
                'description': _.description,
                'category': _.category,
                'price': _.price,
                'count': temp_order[_.title]['count'] if temp_order.keys().__contains__(_.title) else 0,
            }
        })
    # ----------------------------------------
    return render(request, 'order.html', {
        'Items': items,
        'range': range_,
    })


# ajax has to take care of the order changes and update the Pickle file
def ajax_order(request):
    data_json = json.loads("{" + request.GET['data'] + "}")
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            unserialized_data = pickle.load(handle)
        data = unserialized_data
    except:
        data = {}
    data.update(data_json)
    try:
        # Store data (serialize)
        with open(request.session.session_key + '.pickle', 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    except:
        "write error"
    return JsonResponse(data)


# ------------------------------------------------------------------------------------------
# If number of items is zero, then remove the items
@login_required
def cart_page(request):
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            temp_order = pickle.load(handle)
    except:
        temp_order = {}
    vendor = Vendor.objects.get(profile__user__username="msohani")
    items_from_vendor = vendor.item.all()
    cart = {}
    total_items = 0
    total_price = 0
    for _ in temp_order:
        try:
            if temp_order.get(_)['count']:
                item = items_from_vendor.get(title=_)
                total_items = total_items + temp_order.get(_)['count']
                total_price = total_price + temp_order.get(_)['count'] * item.price
                cart.update({
                    item.title: {
                        'title': item.title,
                        'price': item.price,
                        'count': temp_order.get(_)['count'],
                        'description': item.description,
                        'category': item.category,
                        'total_price': item.price * temp_order.get(_)['count'],
                    }
                })
        except:
            pass
    cart.update({
        'total_items': total_items,
        'total_price': total_price,
    })
    print(cart)
    return render(request, 'cart.html', {
        'Items': cart,
        'phone_number': vendor.profile.phone_number,
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
