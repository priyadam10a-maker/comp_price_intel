from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/',views.register,name='register'),
    path('login/',views.login_view,name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout_view,name='logout'),
    path('search-product/',views.search_product,name='search_product'),
    path('category-suggestions/',views.category_suggestions,name='category_suggestions'),
    path('brand-suggestions/',views.brand_suggestions,name='brand_suggestions'),
    path('product-suggestions/',views.product_suggestions,name='product_suggestions'),
    path('feature-suggestions/',views.feature_suggestions,name='feature_suggestions'),
    path('start-scraping/',views.start_scraping,name='start_scraping'),
]