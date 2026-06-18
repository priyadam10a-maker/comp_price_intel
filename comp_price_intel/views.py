from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import (
    User, Product, Category, Brand, ProductSpecification, UserProduct,
    CompetitorProduct, ProductMatch, PricingRecommendation, Inventory, ProductDemand
)
import json
import jwt
from datetime import datetime,timedelta
from django.conf import settings
from django.http import HttpResponse,JsonResponse
from django.db.models import Avg
import threading
import random
import time
from decimal import Decimal
from django.utils import timezone

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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
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

    user_obj = User.objects.filter(user_id=payload["user_id"]).first()
    total_products = UserProduct.objects.filter(user=user_obj).count() if user_obj else 0
    competitors_tracked = CompetitorProduct.objects.count()
    recommendations_generated = PricingRecommendation.objects.count()
    
    # Calculate average demand
    avg_demand_rec = PricingRecommendation.objects.aggregate(avg=Avg('demand_score'))['avg']
    avg_demand_score = round(float(avg_demand_rec), 2) if avg_demand_rec else 0.00
    
    # Calculate low stock count
    low_stock_count = PricingRecommendation.objects.filter(inventory_level__lt=15).count()

    return render(request, "dashboard.html", {
        "user_name": display_name,
        "total_products": total_products,
        "competitors_tracked": competitors_tracked,
        "recommendations_generated": recommendations_generated,
        "avg_demand_score": avg_demand_score,
        "low_stock_count": low_stock_count
    })

def logout_view(request):
    response=redirect("login")
    response.delete_cookie("jwt_token")
    return response

def products(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")

    all_products = Product.objects.select_related('brand', 'category').all()
    if request.method == "POST":
        category = request.POST.get("category")
        brand = request.POST.get("brand")
        product_name = request.POST.get("product")
        
        if category:
            all_products = all_products.filter(category__category_name__icontains=category)
        if brand:
            all_products = all_products.filter(brand__brand_name__icontains=brand)
        if product_name:
            all_products = all_products.filter(product_name__icontains=product_name)

    return render(request, "products.html", {"products": all_products})

def run_real_scrape(product_id):
    try:
        product = Product.objects.get(product_id=product_id)
        
        # Real scraping integration would go here. 
        # For now, we've removed the mock data generation as requested.
        print(f"Triggered real scrape sequence for {product.product_name}")
        
    except Product.DoesNotExist:
        pass

def generate_pricing_recommendations(product, competitors):
    if not competitors:
        return
        
    prices = [c.listed_price for c in competitors if c.listed_price]
    if not prices:
        return
        
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    
    # Mock demand and inventory
    demand_score = Decimal(str(round(random.uniform(30.0, 95.0), 2)))
    inventory = random.randint(5, 100)
    
    # Simple algorithm
    if inventory > 50 and demand_score < 50:
        strategy = "Penetration Pricing"
        recommended_price = min_price - Decimal('1.00')
        reason = f"High inventory ({inventory}) and low demand. Undercutting lowest competitor (${min_price}) to clear stock."
    elif demand_score > 80:
        strategy = "Premium Pricing"
        recommended_price = max_price + Decimal('2.00')
        reason = f"High demand score ({demand_score:.1f}). Setting premium above highest competitor (${max_price})."
    elif inventory < 15:
        strategy = "Skimming Pricing"
        recommended_price = max_price - Decimal('0.50')
        reason = f"Low stock ({inventory}). Matching high end to maximize profit."
    else:
        strategy = "Competitive Pricing"
        recommended_price = avg_price
        reason = f"Stable market. Matching average competitor price (${avg_price:.2f})."
        
    PricingRecommendation.objects.create(
        product=product,
        current_price=product.current_price,
        average_competitor_price=avg_price,
        lowest_competitor_price=min_price,
        highest_competitor_price=max_price,
        demand_score=demand_score,
        inventory_level=inventory,
        recommended_price=recommended_price,
        pricing_strategy=strategy,
        recommendation_reason=reason,
        generated_at=timezone.now()
    )

def product_detail(request, product_id):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")
    
    try:
        product = Product.objects.get(product_id=product_id)
        competitors = CompetitorProduct.objects.filter(product=product)
        
        # Map platform_ids to actual platform names based on scrapers
        platform_mapping = {
            1: "Amazon",
            2: "Flipkart",
            3: "Toolsvilla",
            4: "Industry Buying"
        }
        
        for comp in competitors:
            comp.platform_name = platform_mapping.get(comp.platform_id, f"Platform {comp.platform_id}")
            
        recommendation = None
        
        context = {
            "product": product,
            "competitors": competitors,
            "recommendation": recommendation
        }
        return render(request, "product_details.html", context)
    except Product.DoesNotExist:
        return redirect("products")

def scrape_logs(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")
        
    logs = CompetitorProduct.objects.select_related('product').order_by('-last_scraped')[:50]
    return render(request, "scrape_logs.html", {"logs": logs})

def category_suggestions(request):
    query = request.GET.get("q", "")
    categories = Category.objects.filter(category_name__icontains=query)[:10]
    data = [category.category_name for category in categories]
    return JsonResponse(data, safe=False)

def brand_suggestions(request):
    query = request.GET.get("q","")
    brands = Brand.objects.filter(brand_name__icontains=query)[:10]
    data = [brand.brand_name for brand in brands]
    return JsonResponse(data,safe=False)

def product_suggestions(request):
    query = request.GET.get("q","")
    products = Product.objects.filter(product_name__icontains=query)[:10]
    data = [product.product_name for product in products]
    return JsonResponse(data,safe=False)

def feature_suggestions(request):
    query = request.GET.get("q","")
    features = ProductSpecification.objects.filter(specification_name__icontains=query)[:10]
    data = [feature.specification_name for feature in features]
    return JsonResponse(data,safe=False)

def start_scraping(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")
        
    product_id = request.POST.get("product_id")
    if product_id:
        thread = threading.Thread(target=run_real_scrape, args=(product_id,))
        thread.start()
        
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)

def your_products(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")
    
    try:
        user = User.objects.get(user_id=payload["user_id"])
        products = UserProduct.objects.filter(user=user).select_related('brand', 'category')
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
                quantity_available=data.get("quantity_available") or None,
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
            product.quantity_available = data.get("quantity_available") or None
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


# ─── NEW VIEWS ────────────────────────────────────────────────────────────────

def competitor_analysis(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")

    # Fetch all product matches joined with competitor product info
    matches = (
        ProductMatch.objects
        .select_related('product', 'competitor_product')
        .order_by('-similarity_score')
    )

    return render(request, "competitor_analysis.html", {"matches": matches})


def pricing_recommendations(request):
    payload = verify_jwt(request)
    if not payload:
        return redirect("login")

    recommendations = (
        PricingRecommendation.objects
        .select_related('product')
        .order_by('-generated_at')
    )

    return render(request, "pricing_recommendations.html", {"recommendations": recommendations})

def run_analytics_for_products(product_ids, user_id):
    import time
    from database.db_connection import get_connection
    from analytics.recommendation_engine import generate_recommendation
    from analytics.save_recommendation import save_recommendation
    
    time.sleep(1)
    
    conn = get_connection()
    if not conn:
        print("Failed to get DB connection for analytics")
        return
        
    try:
        cursor = conn.cursor(dictionary=True)
        for pid in product_ids:
            up = UserProduct.objects.filter(user_product_id=pid, user_id=user_id).first()
            if not up:
                continue
                
            current_price = float(up.current_price) if up.current_price else 0.0
            
            # Fetch actual inventory
            from comp_price_intel.models import Inventory, ProductDemand
            inv_obj = Inventory.objects.filter(product_id=pid).first()
            inv_level = inv_obj.quantity_available if inv_obj and inv_obj.quantity_available is not None else 0
            
            # Fetch actual demand
            dem_obj = ProductDemand.objects.filter(product_id=pid).first()
            dem_score = float(dem_obj.demand_score) if dem_obj and dem_obj.demand_score is not None else 0.0
            
            try:
                rec = generate_recommendation(cursor, pid, current_price)
                save_recommendation(
                    cursor=cursor,
                    user_product_id=pid,
                    current_price=current_price,
                    recommended_price=rec["recommended_price"],
                    demand_score=dem_score,
                    inventory_level=inv_level,
                    strategy=rec.get("strategy", "Parity Pricing"),
                    reason="", # Removed reason per user request
                    avg_comp_price=rec.get("parity_price"),
                    min_comp_price=rec.get("parity_price"),
                    max_comp_price=rec.get("parity_price"),
                    parity_price_calc=rec.get("parity_price"),
                    inventory_price_calc=rec.get("inventory_price"),
                    demand_price_calc=rec.get("demand_price")
                )
            except Exception as e:
                print(f"Error processing pid {pid}: {e}")
            
        conn.commit()
    except Exception as e:
        print(f"Error in analytics: {e}")
    finally:
        cursor.close()
        conn.close()

def start_analysis(request):
    payload = verify_jwt(request)
    if not payload:
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_ids = data.get("product_ids", [])
            user = User.objects.get(user_id=payload["user_id"])
            
            thread = threading.Thread(target=run_analytics_for_products, args=(product_ids, user.user_id))
            thread.start()
            
            return JsonResponse({"message": "Analysis started successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request"}, status=400)