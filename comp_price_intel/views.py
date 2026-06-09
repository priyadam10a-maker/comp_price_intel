from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import User
import jwt
from datetime import datetime,timedelta
from django.conf import settings
from django.http import HttpResponse

def home(request):
    return render(request,'home.html')
def register(request):
    if request.method=="POST":
        full_name=request.POST.get("full_name")
        email=request.POST.get("email")
        password=request.POST.get("password")
        password_confirm=request.POST.get("password_confirm")

        print("Password:", password)
        print("Confirm:", password_confirm)

        if password!=password_confirm:
            return render(request,"register.html",{"error":"Passwords do not match"})
        if User.objects.filter(email=email).exists():
            return render(request,"register.html",{"error":"Email already exists"})
        User.objects.create(
            full_name=full_name,
            email=email,
            password_hash=make_password(password),
            role="Analyst"
        )
        return redirect("login")
    return render(request,"register.html")

def login_view(request):
    if request.method=="POST":
        email=request.POST.get("email")
        password=request.POST.get("password")
        
        try:
            user=User.objects.get(email=email)
            print("User found:", user.email)
            if check_password(password,user.password_hash):
                print("Password matched")
                
                payload={
                    "user_id":user.user_id,
                    "email":user.email,
                    "role":user.role,
                    "exp":datetime.utcnow()+timedelta(hours=1),
                }
                token=jwt.encode(
                    payload,
                    settings.SECRET_KEY,
                    algorithm="HS256"
                )
                response=redirect("dashboard")

                response.set_cookie(
                    "jwt_token",
                    token,
                    httponly=True,  
                )
                return response
            
            else:
                print("Password NOT matched")
                return render(request,"login.html",{"error":"Invalid Password"})
            
        except User.DoesNotExist:
            print("User not found")
            return render(request,"login.html",{"error":"Email not found"})
        
    return render(request,"login.html")

def verify_jwt(request):

    token = request.COOKIES.get("jwt_token")

    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        return payload

    except jwt.ExpiredSignatureError:
        return None

    except jwt.InvalidTokenError:
        return None

def dashboard(request):

    payload = verify_jwt(request)

    if not payload:
        return redirect("login")

    return render(
        request,
        "dashboard.html",
        {
            "user_name": payload["email"]
        }
    )

def logout_view(request):
    response=redirect("login")
    response.delete_cookie("jwt_token")
    return response