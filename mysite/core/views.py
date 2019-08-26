import random
import re
import time
import json
import pickle

import googlemaps
import stripe
from django.contrib.auth import login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from path import Path
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from mysite import settings
from mysite.core.models import Profile, Vendor, Order
from twilio.rest import Client
from mysite.core.tokens import account_activation_token, sms_activation_token
from mysite.forms import UserForm, ProfileForm, SignUpForm
from django.contrib.auth.decorators import user_passes_test


# Secret code used in urls
class urlsecret:
    SECRET_CODE = 'BNcNKV0mXuSTKNMKc10TFuMcXmQK5kGSuTXKdslzNEo63JjTfcmwR9Tv6zbdZz36'


stripe.api_key = settings.STRIPE_SECRET_KEY  # new


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def handler403(request):
    return render(request, '403.html', status=403)


# --------------------------------  USER_PASSES_TEST FUNCTION DEFINITIONS -------------------------------
def is_user_email_verified(user):
    """
    This is @user_passes_test function. Checks if user has verified email
    e.g: @user_passes_test(is_user_email_verified, login_url='/home/', redirect_field_name='HOME_REDIRECT_URL')
    :param:
    user: username from request.user
    :return:
    a Boolean showing if user's email is verified (==2)
    """
    profile = Profile.objects.get(user__username=user)
    return profile.email_verification_status == 2


def is_user_phone_verified(user):
    """
    This is @user_passes_test function. Checks if user has verified phone number
    e.g: @user_passes_test(is_user_phone_verified, login_url='/home/', redirect_field_name='HOME_REDIRECT_URL')
    :param:
    user: username from request.user
    :return:
    a Boolean showing if user's phone number is verified (==2)
    """
    profile = Profile.objects.get(user__username=user)
    return profile.phone_verification_status == 2


def user_phone_verification_sent(user):
    """
    This is @user_passes_test function. Checks if user phone verification message has already been sent
    :param
    user: username from request.user
    :return:
    a boolean showing if user's phone number is verified (==1)
    """
    profile = Profile.objects.get(user__username=user)
    return profile.phone_verification_status == 1


def user_phone_verification_never_sent(user):
    """
    This is @user_passes_test function. checks if user phone verification message has never been sent
    :param user:
    :return:
    """
    profile = Profile.objects.get(user__username=user)
    return profile.phone_verification_status == 0


def is_user_fully_registered(user):
    """
    Tests if user has fully entered all required information and filled his profile.
    :param
    user: username from request .user
    :return:
    boolean with Profile.profile_filled
    """
    profile = Profile.objects.get(user__username=user)
    return profile.profile_filled


# --------------------------------- END_USER_PASSES_TEST ------------------------------------------------

# ----------------   Chronological login process   -----------------------------------------
# ------------------------------------------------------------------------------------------
def signup(request):
    """
    Registers user's profile information such as Address, Phone, etc
    # after login, user is redirected to signup to check if all information for user is registered, first time user
    # registers and logs in, specially after logging in with OAuth, he has to fill in registration form in "signup"
    # page. There is will be a bit (user_is_registered) in registration Model which will be set when user registers
    # all information
    # partially taken from : https://frfahim.github.io/post/django-registration-with-confirmation-email/
    # and from https://simpleisbetterthancomplex.com/tutorial/2016/06/27/how-to-use-djangos-built-in-login-system.html
    :param
    request: HTTP request
    :return: returns a page stating that an email confirmation has been sent to the user, for confirmation
    """
    # have to add Error message if email is not available -> maybe a User_Pass_test function
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            # Set email_verification to 0
            profile = Profile.objects.get(user__username=user.username)
            profile.email_verification_status = 0  # means email verification has been started
            profile.save()
            # Create email message
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,  # have to change this??
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # return render(request, 'confirm_email.html')
            return redirect('update_profile_after_initial')
    else:
        # Request = GET
        form = SignUpForm
    return render(request, 'registration/signup.html', {
        'form': form
    })


"""        Backup for send_sms function
# -------------------------------------- Send SMS ------------------------------------------------
# @user_passes_test(user_phone_verification_never_sent, login_url='/sms_sent/')  # This should be a page that asks

def send_sms(request):
profile = Profile.objects.get(user__username=request.user)
user = User.objects.get(username=request.user)
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
SMS_MSG = "http://" + message['domain'] + '/phone_activate/' + message['uid'] + "/" + message['token']
client.messages \
    .create(
    body=SMS_MSG,
    from_='+18622608689',
    to=to_phone
)
profile.number_of_sms_sent += 1
profile.save()
return render(request, 'smssent.html')

"""


# -------------------------------------- Send SMS ------------------------------------------------
# @user_passes_test(user_phone_verification_never_sent, login_url='/sms_sent/')  # This should be a page that asks
def send_sms(request):
    """
    Sends text to current user to confirm phone number
    Note 0. Up to 3 text messages can be sent. Code checks the number of text already been sent.
    Note 1. Your Account Sid and Auth Token from twilio.com/console
    Note 2. DANGER! This is insecure. See http://twil.io/secure
    :param request: current HTML request
    :return: HTML page to "smssent.html"
    """

    profile = Profile.objects.get(user__username=request.user)
    to_phone = profile.phone_number
    account_sid = 'AC8a77fcba5f491b28d836d503873525a4'
    auth_token = 'ed2108cb7b1f056cc6c2a3ff29fed267'
    client = Client(account_sid, auth_token)
    profile.phone_verification_code = random.randint(111111, 999999)
    message = {
        'token': "Your verification code is: " + str(profile.phone_verification_code),
    }
    SMS_MSG = message['token']
    """
    client.messages \
        .create(
        body=SMS_MSG,
        from_='+18622608689',
        to=to_phone
    )
    """
    profile.number_of_sms_sent += 1
    profile.save()
    return render(request, 'smssent.html')


def sms_sent(request):
    """
    Opens HTML page with "text sent" information
    :param request: .
    :return: HTML smssent.html page
    """
    return render(request, 'smssent.html')


def phone_activate(request, uidb64, token):
    """
    Activates (changes Profile.phone_verification_status). The main function used is in token.py file
    It verifies if the generated code, clicked is right one
    :param request: HTML request
    :param uidb64: Coded User.PK id
    :param token: generated token from timestamp
    :return: returns a message showing if the verification code was right or not.
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and sms_activation_token.check_token(user, token):
        profile_ = Profile.objects.get(user__username=user)
        profile_.phone_verification_status = 2
        profile_.save()
        logout(request)
        return HttpResponse('<p> Thank you for your phone confirmation. Now you can login your account. </p>')
    else:
        return HttpResponse('<p> Activation link is invalid! You can request another message by logging in </p>')


# --------------------------------------- End Send SMS -----------------------------------------


# --------------------------------------- Send Email Activation --------------------------------
def send_email_confirmation(request):
    """
    Sends email confirmation per user request in case user has not received confirmation email yet
    :param request:
    :return: renders the confirmation for email page
    """
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
    return redirect('home')
    # return render(request, 'confirm_email.html')


def confirm_email_sent(request):
    return render(request, 'confirm_email.html')


def activate(request, uidb64, token):
    """

    :param request:
    :param uidb64:
    :param token:
    :return:
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        profile_ = Profile.objects.get(user__username=user.username)
        profile_.email_verification_status = 2
        profile_.save()
        # login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        # logout(request)
        return HttpResponse("Thank you for your email confirmation. If you haven't confirmed your phone number yet, "
                            "do so by "
                            "requesting a phone confirmation and clicking on the link in your text message")
    else:
        return HttpResponse('Activation link is invalid! You can send another request in your home page')


# ------------------------------------------------------------------------------------------
@login_required
@user_passes_test(is_user_fully_registered, login_url='/' + urlsecret.SECRET_CODE + '/account/update_profile/')
# @user_passes_test(is_user_email_verified, login_url='/resendemailconfirmation/')  # This should be a page that asks
# @user_passes_test(is_user_phone_verified, login_url='/sms/')
def home(request):
    """

    :param request:
    :return:
    """
    # home page: show only when user is logged in, otherwise go to sigin page
    if request.user.is_authenticated:
        profile = Profile.objects.get(user__username=request.user.username)
        user_ = User.objects.get(username=request.user.username)
        order = Order.objects.filter(client__user__username=request.user.username)
        return render(request, 'home.html', {
            'isPhoneVerified': profile.phone_verification_status,
            'isEmailVerified': profile.email_verification_status,
            'firstname': request.user.first_name,
            'lastname': request.user.last_name,
            'orders': order,
            'number_of_items': get_number_of_items_in_cart(request),

        })
    else:
        return redirect('login')


# ------------------------------------------------------------------------------------------
@login_required
def profile(request):
    profile = Profile.objects.get(user__username=request.user.username)
    user = User.objects.get(username=request.user.username)
    return render(request, 'profile.html', {
        'isPhoneVerified': profile.phone_verification_status,
        'isEmailVerified': profile.email_verification_status,
        'firstname': user.first_name,
        'lastname': user.last_name,
        'email': user.email,
        'phone': profile.phone_number,
        'street1': profile.street1,
        'street2': profile.street2,
        'city': profile.city,
        'state': profile.state,
        'zip': profile.zip_code,
        'number_of_items': get_number_of_items_in_cart(request),

    })


@transaction.atomic
# @user_passes_test(is_user_email_verified, login_url='/resendemailconfirmation/')
@login_required
def update_profile(request):
    """
    :param request:
    :return:
    """
    print(request.method)
    if request.method == 'POST':
        print('update_profile check 7')
        print(request.POST)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        print('update_profile check 8')
        print(user_form.is_valid())
        print(profile_form.is_valid())
        if user_form.is_valid() and profile_form.is_valid():
            print('update_profile check 9')
            user_form_data = user_form.cleaned_data
            profile_form_data = profile_form.cleaned_data
            profile_ = Profile.objects.get(user__username=request.user)
            user_ = User.objects.get(username=request.user)
            pre_form_change_email = user_.email
            pre_form_change_phone = profile_.phone_number
            user_form.save()
            print('update_profile check 1')
            profile_form.save()
            profile_ = Profile.objects.get(user=request.user)
            profile_.profile_filled = True
            print('update_profile check 3')
            if pre_form_change_email != user_form_data['email']:
                print('update_profile check 2')
                profile_.email_verification_status = 0
                # Here we have to set a bit in User model that shows we have to confirm user's email
            print('update_profile check 4')
            if pre_form_change_phone != profile_form_data['phone_number']:
                print('update_profile check 5')
                profile_.phone_verification_status = 0
            print('update_profile check 6')
            profile_.profile_filled = True
            profile_.save()
            return redirect('profile')
        else:
            return redirect('update_profile')
    else:
        profile_ = Profile.objects.get(user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'isEmailVerified': profile_.email_verification_status,
    })


# ------------------------------------------------------------------------------------------
# @user_passes_test(is_user_email_verified, redirect_field_name='/resendemailconfirmation/')
# @user_passes_test(is_user_phone_verified, redirect_field_name='/sms/')
def update_profile_after_initial(request):
    """

    :param request:
    :return:
    """
    profile_ = Profile.objects.get(user=request.user)
    profile_.profile_filled = False
    profile_.save()
    return redirect('update_profile')


# ------------------------------------------------------------------------------------------
def register(request):
    """

    :param request:
    :return:
    """
    return redirect(update_profile_after_initial)


# ------------------------------------------------------------------------------------------
@login_required
def signup_additional(request):
    """

    :param request:
    :return:
    """
    return render(request, 'registration/signup_additional.html')


# Second way to create secret page
# class SecretPage(LoginRequiredMixin, TemplateView):
#    template_name = '*.html'


# deletes .pickle files older than one day
def delete_files():
    """

    :return:
    """
    d = Path("mysite/..")
    for i in d.walk():
        if i.endswith(".pickle"):
            days = 30
            time_in_secs = time.time() - (days * 24 * 60 * 60)
            if i.isfile():
                if i.mtime <= time_in_secs:
                    i.remove()


# ------------------------------------------------------------------------------------------
# Only GET method. The submit button only refers to "CART" page.
# the rest of this function takes care of finding vendor and associated profile
@login_required
@user_passes_test(is_user_email_verified, login_url='/' + urlsecret.SECRET_CODE + '/sendemailconfirmation/')
@user_passes_test(is_user_phone_verified, login_url='/' + urlsecret.SECRET_CODE + '/sms/')
def order_page(request):
    """

    :param request:
    :return:
    """
    print("in order_page")
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
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            unserialized_data = pickle.load(handle)
        temp_order = unserialized_data
    except:
        temp_order = {}
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
        'number_of_items': get_number_of_items_in_cart(request),
    })


# ajax has to take care of the order changes and update the Pickle file
def ajax_order(request):
    """

    :param request:
    :return:
    """
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
    data.update({
        'number_of_items': get_number_of_items_in_cart(request),
    })
    return JsonResponse(data)


def ajax_sms(request):
    """

    :param request:
    :return:
    """
    data_json = json.loads(request.GET['data'])
    print(data_json)
    data = {}
    profile = Profile.objects.get(user__username=request.user)
    data.update({
        'data': profile.phone_verification_code,
    })
    return JsonResponse(data)


"""
def profile_ajax(request):
/// Comments
Checks all inputs from profile_update page
:param request:
:return:
////
print(request.GET)
email = request.GET['email']
print(email)
# check if this email already exists
user_ = User.objects.filter(email=email)
if user_:
    return JsonResponse({'data': 'Another user with the same email is registered'})
else:
    return JsonResponse({'data': ''})
print(user_)
print(not user_)
data = {}
profile = Profile.objects.get(user__username=request.user)
data.update({
    'data': profile.phone_verification_code,
})
return JsonResponse(data)
"""


def order_history(request):
    return render(request, 'order_history.html')


def profile_check_ajax(request):
    print(request.GET)
    phone_number = request.GET['phone_number']
    zip_code = request.GET['zip_code']
    print(phone_number)
    data = {}
    if re.match(r'^[2-9]\d{2}-\d{3}-\d{4}$', phone_number):
        data.update({
            'phone_number': 'correct',
        })
    else:
        data.update({
            'phone_number': 'incorrect',
        })
    if re.match(r'^[0-9]\d{4}$', zip_code):
        data.update({
            'zip_code': 'correct',
        })
    else:
        data.update({
            'zip_code': 'incorrect',
        })
    return JsonResponse(data)


# ------------------------------------------------------------------------------------------
# If number of items is zero, then remove the items
@login_required
def cart_page(request):
    """

    :param request:
    :return:
    """
    items_from_form = {}
    if request.method == "POST":
        items_from_form = request.POST
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            temp_order = pickle.load(handle)
    except:
        temp_order = {}
    for _ in temp_order:
        try:
            if items_from_form.get(_):
                temp_order.update({
                    _: {
                        'count': int(items_from_form.get(_))},
                })
        except:
            pass
    # this has to be the vendor assigned to the client
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
        try:
            # Store data (serialize)
            with open(request.session.session_key + '.pickle', 'wb') as handle:
                pickle.dump(temp_order, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except:
            "write error"
    cart.update({
        'total_items': total_items,
        'total_price': total_price,
    })
    return render(request, 'cart.html', {
        'Items': cart,
        'number_of_items': get_number_of_items_in_cart(request),

    })


# ------------------------------------------------------------------------------------------
def checkout(request):
    """

    :param request:
    :return:
    """
    pass


# ------------------------------------------------------------------------------------------
class pay(TemplateView):
    """

    """
    template_name = 'payment.html'

    def get_context_data(self, **kwargs):  # new
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


# ------------------------------------------------------------------------------------------
def charged(request):  # new
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=500,
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        return render(request, 'charged.html')


def logout(request):
    return redirect('/accounts/logout/')


def get_number_of_items_in_cart(request):
    try:
        with open(request.session.session_key + '.pickle', 'rb') as handle:
            temp_order = pickle.load(handle)
    except:
        temp_order = {}
    total_items = 0
    for _ in temp_order:
        try:
            if temp_order.get(_)['count']:
                total_items = total_items + temp_order.get(_)['count']
        except:
            pass
    return total_items


def support(request):
    vendor = Vendor.objects.get(profile__user__username="msohani")
    return render(request, 'support.html', {
        'phone_number': vendor.profile.phone_number,

    })
