
import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.urls import reverse
from django.views.decorators.http import require_POST
from validate_email_address import validate_email
from django.contrib import messages
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from userpreference.models import *
from .token import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate ,login ,logout
import threading

def email_thread(email):
    def send_email():
        email.send(fail_silently=False)

    t = threading.Thread(target=send_email)
    t.start()

    


# Create your views here.
def Login(request):
    page= 'login'
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'Username not found')
        
        user = authenticate(username=username,password=password)
        if user is not None and user.is_active:
            login(request,user)
            return redirect('index')
        else:
            messages.error(request,"Invalid Credentials")
        
    context ={'page':page}
    return render(request,'authentication/login_register.html',context)

def Logout(request):
    logout(request)
    messages.info(request,"Logout Sucessfull")
    return redirect('index')
    

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect('login')


def activate_email(request , user , to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("authentication/account_activation.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email_thread(email):
        messages.success(request, f'Dear {user} , please go to you email {to_email}  inbox and click on \
                received activation link to confirm and complete the registration. Note:  Check your spam folder.')
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')

def Registration(request):
    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    context={'fieldValues':request.POST}
                    messages.error(request,'Password is short')
                    return render(request,'authentication/login_register.html',context)
            
            user = User.objects.create_user(username=username,email=email)

            user.set_password(password)
            user.is_active = False
            user.save()
            activate_email(request , user , email)
            return redirect('index')
        
    return render(request,'authentication/login_register.html')

@require_POST
def username_validation(request):
    data = json.loads(request.body)
    username = data['username']

    if not str(username).isalnum():
        return JsonResponse({'username_error':'Username should only contain alphanumeric characters'}, status=400)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'username_error':'Username is already taken '}, status=400)
   
    return JsonResponse({'username_valid':True})

@require_POST
def email_validation(request):
    data = json.loads(request.body)
    email = data['email']

    if not validate_email(email):
        return JsonResponse({'email_error':'Email Pattern Wrong'}, status=400)
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({'email_error':'Email is already registered'},status=409)
    
    return JsonResponse({'email_valid':True})

@require_POST
def password_validation(request):
    data = json.loads(request.body)
    password1 = data['password1']
    password = data['password']

    if password != password1 :
        return JsonResponse({'password_error': 'Password doesnot match' }, status=400)
    
    return JsonResponse({'password_valid':True})


def ResetPassword(request):
    if request.method =="POST":
        email = request.POST['email']

        context={
            'values':request.POST
        }

        if not validate_email(email):
            messages.success(request,'Email is invalid')
            return render(request,'authentication/reset-password.html',context)
        
        if not  User.objects.filter(email=email).exists():
            messages.success(request,'Enter the correct emailaddress')
            return render(request,'authentication/reset-password.html',context)

        current_site = get_current_site(request)

        user = get_user_model().objects.filter(email=email)
        if user.exists():
            email_content = {
                        'user': user[0],
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                        'token': PasswordResetTokenGenerator().make_token(user[0]),
                    }

            link = reverse('set-password', kwargs={
                                'uidb64': email_content['uid'], 'token': email_content['token']})

            email_subject = 'Activate your account'

            reset_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                        email_subject,
                        'Hi '+ ', Please the link below to set your password \n'+reset_url,
                        'noreply@semycolon.com',
                        [email],
                    )
            email_thread(email)
            messages.success(request,'Check Your Mail to set a new password')

    return render(request,'authentication/reset-password.html')


def set_password(request , uidb64 ,token):
    if request.method == "GET":

        context={
                'uidb64':uidb64,
                'token':token
            }
        try:
            user_id= urlsafe_base64_decode(uidb64).decode('utf-8')
            user= User.objects.get(pk=user_id)
            
            if not PasswordResetTokenGenerator().check_token(user , token):
                messages.info(request,'Link Already Used.')
                return render(request , 'authentication/reset-password.html',context)
        except User.DoesNotExist:
                messages.info(request, "User does not exist")
        except Exception as e:
                # Log the specific exception to understand the error
                messages.error(request, f"An error occurred: {str(e)}")

        return render(request , 'authentication/set_password.html',context)

    elif request.method == "POST":

        context={
            'uidb64':uidb64,
            'token':token
        }
        password1 = request.POST['password1']
        password = request.POST['password']

    
        if password != password1 :
            messages.error(request,"Passwords don't match")
            return render(request,'authentication/set_password.html',context)
        if len(password) < 6:
                messages.error(request,'Password is short')
                return render(request,'authentication/set_password.html',context)
        
        try:
            user_id= urlsafe_base64_decode(uidb64).decode('utf-8')
            user= User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset Sucessfull')
            return redirect('login')
        except User.DoesNotExist:
            messages.info(request, "User does not exist")
        except Exception as e:
            # Log the specific exception to understand the error
            messages.error(request, f"An error occurred: {str(e)}")

        return render(request , 'authentication/set_password.html',context)
    else:
        return HttpResponse(status=405)



