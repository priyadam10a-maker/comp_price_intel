from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('scrape-logs/', views.scrape_logs, name='scrape_logs'),
    path('category-suggestions/', views.category_suggestions, name='category_suggestions'),
    path('brand-suggestions/', views.brand_suggestions, name='brand_suggestions'),
    path('product-suggestions/', views.product_suggestions, name='product_suggestions'),
    path('feature-suggestions/', views.feature_suggestions, name='feature_suggestions'),
    path('start-scraping/', views.start_scraping, name='start_scraping'),
    path('your-products/', views.your_products, name='your_products'),
    path('competitor-analysis/', views.competitor_analysis, name='competitor_analysis'),
    path('pricing-recommendations/', views.pricing_recommendations, name='pricing_recommendations'),
    path('api/add-user-product/', views.add_user_product, name='add_user_product'),
    path('api/edit-user-product/<int:product_id>/', views.edit_user_product, name='edit_user_product'),
    path('api/delete-user-product/<int:product_id>/', views.delete_user_product, name='delete_user_product'),
    path('api/add-brand/', views.add_brand, name='add_brand'),
    path("api/add-category/", views.add_category, name="add_category"),
    path("api/start-analysis/", views.start_analysis, name="start_analysis"),
]