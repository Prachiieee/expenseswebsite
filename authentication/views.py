from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.contrib import auth
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import token_generator
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .utils import AppTokenGenerator
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading 

# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email=email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class EmailValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error':'Email is inavalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'sorry!! Email is used, choose another one!'}, status=409)
        return JsonResponse({'email_valid': True})
    
class UserNameValidationView(View):
    def post(self, request):
        data=json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error':'username should contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'sorry!! Username is used, choose another one!'}, status=409)
        return JsonResponse({'username_valid': True})

from django.core.mail import send_mail

class RegisterationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')

    def post(self,request):
        #GET USER DATA
        #validates
        #create a user account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context={
            'fieldvalues':request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password)<6:
                    messages.error(request,'password too short')
                    return render(request,'authentication/register.html',context)
                
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active=False
                user.save()
                # path_to_view
                # - getting domain we are on
                # -relative url to verification 
                # -encode uid
                # -token
                uidb64=urlsafe_base64_encode(force_bytes(user.pk))

                domain=get_current_site(request).domain
                link=reverse('active',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})
                email_subject='Activate Your Account'
                active_url='http://'+ domain + link
                email_body='Hii '+ user.username+"Please use this link to verify your account\n"+active_url
                email = EmailMessage(
                        email_subject,
                        email_body,
                        "noreply@semycolon.com",
                        [email],
                    )
                EmailThread(email).start()
                messages.success(request,'Account Successfully Created')
                return render(request,'authentication/register.html')
                

        return render(request,'authentication/register.html')

class VerificationView(View):
    def get(self,request,uidb64,token):
        try:
            id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=id)

            if not AppTokenGenerator.check_token(user, token):
                return redirect('login'+'?message='+'User already activate')

            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()

            messages.success(request,'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass
        
        return redirect('login')
    
class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')
    
    def post(self, request):
        username = request.POST.get('username')  # Use .get() to avoid KeyError
        password = request.POST.get('password')

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome, {user.username}! You are now logged in.')
                    return redirect('expenses')
                messages.error(request, 'Your account is not active. Please check your email to activate it.')
                return render(request, 'authentication/login.html', {'username': username})
            messages.error(request, 'Invalid username or password.')
            return render(request, 'authentication/login.html', {'username': username})

        messages.error(request, 'Please provide both username and password.')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self,request):
        auth.logout(request)
        messages.success(request,'You have been loged Out')
        return redirect('login')
    
class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')
    
    def post(self, request):
        email = request.POST['email']
        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error(request, "Please supply a valid email")
            return render(request, 'authentication/reset-password.html', context)

        # Filter the user
        user = User.objects.filter(email=email).first()  # Get the first matching user or None

        if user:  # Check if a user was found
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # Now user is properly assigned
            domain = get_current_site(request).domain
            link = reverse(
                'reset-user-password',
                kwargs={'uidb64': uidb64, 'token': PasswordResetTokenGenerator().make_token(user)}
            )
            reset_url = 'http://' + domain + link
            email_subject = 'Password reset Instructions'
            email_contents = f"Hi there,\nPlease click the link below to reset your password:\n{reset_url}"

            email_message = EmailMessage(
                email_subject,
                email_contents,
                "noreply@semycolon.com",
                [email],
            )
            EmailThread(email).start()

        # Inform the user regardless of whether the email exists, to prevent account enumeration
        messages.success(request, "We have sent you an email to reset your password")
        return render(request, 'authentication/reset-password.html')

class CompletePasswordReset(View):
    def get(self,request,uidb64,token):

        context={
            'uidb64':uidb64,
            'token':token
        }

        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,"Password link is a Invalid,please request a new One!")
                return render(request, 'authentication/reset-password.html') 
        except Exception as identifier:
            pass
        return render(request,'authentication/set-newpassword.html',context)
    
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }
        password=request.POST['password']
        password2=request.POST['password2']

        if password != password2:
            messages.error(request,"Password do not match")
            return render(request,'authentication/set-newpassword.html',context)
        
        if len(password)<6:
            messages.error(request,"Password too short")
            return render(request,'authentication/set-newpassword.html',context)
        
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.password=password
            user.save()

            messages.success(request,"Password reset successfull,you can login with your new password!")
            return redirect('login')
        except Exception as identifier:
            messages.info(request,"Something Went Wrong!,try Again!!")
            return render(request,'authentication/set-newpassword.html',context)
        
        

        