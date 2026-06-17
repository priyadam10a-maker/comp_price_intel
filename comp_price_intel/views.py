from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import User,Product,Category,Brand,ProductSpecification,UserProduct
import json
import jwt
from datetime import datetime,timedelta
from django.conf import settings
from django.http import HttpResponse,JsonResponse

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

    try:
        user = User.objects.get(user_id=payload["user_id"])
        display_name = user.full_name
    except User.DoesNotExist:
        display_name = payload.get("email", "User")

    return render(
        request,
        "dashboard.html",
        {
            "user_name": display_name
        }
    )

def logout_view(request):
    response=redirect("login")
    response.delete_cookie("jwt_token")
    return response

def search_product(request):

    payload = verify_jwt(request)

    if not payload:
        return redirect("login")

    if request.method == "POST":

        category = request.POST.get("category")
        brand = request.POST.get("brand")
        product_name = request.POST.get("product")
        feature = request.POST.get("feature")

        print("Category:", category)
        print("Brand:", brand)
        print("Product:", product_name)
        print("Feature:", feature)

        try:

            product = Product.objects.get(
                product_name=product_name
            )

            return render(
                request,
                "product_details.html",
                {
                    "product": product
                }
            )

        except Product.DoesNotExist:

            return render(
                request,
                "search_product.html",
                {
                    "error": "Product not found"
                }
            )

    return render(
        request,
        "search_product.html"
    )

def category_suggestions(request):

    query = request.GET.get("q", "")

    categories = Category.objects.filter(
        category_name__icontains=query
    )[:10]

    data = [
        category.category_name
        for category in categories    
    ]

    return JsonResponse(data, safe=False)

def brand_suggestions(request):

    query = request.GET.get("q","")

    brands = Brand.objects.filter(
        brand_name__icontains=query
    )[:10]

    data = [
        brand.brand_name
        for brand in brands
    ]

    return JsonResponse(data,safe=False)

def product_suggestions(request):

    query = request.GET.get("q","")

    products = Product.objects.filter(
        product_name__icontains=query
    )[:10]

    data = [
        product.product_name
        for product in products
    ]

    return JsonResponse(data,safe=False)

def feature_suggestions(request):

    query = request.GET.get("q","")

    features = ProductSpecification.objects.filter(
        specification_name__icontains=query
    )[:10]

    data = [
        feature.specification_name
        for feature in features
    ]

    return JsonResponse(data,safe=False)

def start_scraping(request):

    payload = verify_jwt(request)

    if not payload:
        return redirect("login")

    product_id = request.POST.get(
        "product_id"
    )

    return HttpResponse(
        f"Scraping started for Product ID {product_id}"
    )

def your_products(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")
    
    try:
        user = User.objects.get(user_id=payload["user_id"])
        products = UserProduct.objects.filter(user=user)
    except User.DoesNotExist:
        return redirect("login")
        
    return render(request, "your_products.html", {"products": products})

def add_user_product(request):
    payload = verify_jwt(request)
    if not payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = User.objects.get(user_id=payload["user_id"])
            
            brand_name = data.get("brand")
            category_name = data.get("category")
            
            brand = Brand.objects.filter(brand_name=brand_name).first()
            if not brand:
                brand = Brand.objects.create(brand_name=brand_name)
                
            category = Category.objects.filter(category_name=category_name).first()
            if not category:
                return JsonResponse({"error": "Please select a valid category"}, status=400)
                
            UserProduct.objects.create(
                user=user,
                product_name=data.get("product_name"),
                brand=brand,
                category=category,
                model_number=data.get("model_number"),
                current_price=data.get("current_price") or None
            )
            return JsonResponse({"message": "Product added successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def edit_user_product(request, product_id):
    payload = verify_jwt(request)
    if not payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    if request.method in ["PUT", "POST"]:
        try:
            data = json.loads(request.body)
            user = User.objects.get(user_id=payload["user_id"])
            product = UserProduct.objects.get(user_product_id=product_id, user=user)
            
            brand_name = data.get("brand")
            category_name = data.get("category")
            
            brand = Brand.objects.filter(brand_name=brand_name).first()
            if not brand:
                brand = Brand.objects.create(brand_name=brand_name)
                
            category = Category.objects.filter(category_name=category_name).first()
            if not category:
                return JsonResponse({"error": "Please select a valid category"}, status=400)
                
            product.product_name = data.get("product_name")
            product.brand = brand
            product.category = category
            product.model_number = data.get("model_number")
            product.current_price = data.get("current_price") or None
            product.save()
            
            return JsonResponse({"message": "Product updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def delete_user_product(request, product_id):
    payload = verify_jwt(request)
    if not payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    if request.method == "DELETE":
        try:
            user = User.objects.get(user_id=payload["user_id"])
            product = UserProduct.objects.get(user_product_id=product_id, user=user)
            product.delete()
            return JsonResponse({"message": "Product deleted successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def add_brand(request):
    payload = verify_jwt(request)
    if not payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            brand_name = data.get("brand_name")
            if not Brand.objects.filter(brand_name=brand_name).exists():
                Brand.objects.create(brand_name=brand_name)
            return JsonResponse({"message": "Brand added successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)

def add_category(request):
    payload = verify_jwt(request)
    if not payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            category_name = data.get("category_name")
            if not Category.objects.filter(category_name=category_name).exists():
                Category.objects.create(category_name=category_name)
            return JsonResponse({"message": "Category added successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)