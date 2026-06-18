from django.db import models

# Create your models here.
class User(models.Model):
    user_id=models.AutoField(primary_key=True)
    full_name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    password_hash=models.CharField(max_length=255)
    role=models.CharField(max_length=20,default='Analyst')
    last_login=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField()
    class Meta:
        db_table='users'
        managed=False

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    class Meta:
        db_table = "categories"
        managed = False
    def __str__(self):
        return self.category_name
    
class Brand(models.Model):
    brand_id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=100)
    country_of_origin = models.CharField(max_length=100,null=True,blank=True)
    website = models.CharField(max_length=255,null=True,blank=True)
    class Meta:
        db_table = "brands"
        managed = False
    def __str__(self):
        return self.brand_name
    
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.DO_NOTHING,
        db_column='brand_id'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        db_column='category_id'
    )
    model_number = models.CharField(max_length=150,null=True,blank=True)
    current_price = models.DecimalField(max_digits=10,decimal_places=2,null=True)
    average_rating = models.DecimalField(max_digits=3,decimal_places=2,null=True)
    total_reviews = models.IntegerField(null=True)
    class Meta:
        db_table = "products"
        managed = False
    def __str__(self):
        return self.product_name

class ProductSpecification(models.Model):
    spec_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(
        Product,
        on_delete=models.DO_NOTHING,
        db_column='product_id'
    )
    specification_name = models.CharField(max_length=100)
    specification_value = models.CharField(max_length=255,null=True,blank=True)
    class Meta:
        db_table = "product_specifications"
        managed = False
    def __str__(self):
        return self.specification_name

class UserProduct(models.Model):
    user_product_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='user_id'
    )
    product_name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.DO_NOTHING,
        db_column='brand_id'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.DO_NOTHING,
        db_column='category_id'
    )
    quantity_available = models.IntegerField(null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "user_products"
        managed = False
        
    def __str__(self):
        return self.product_name

class CompetitorProduct(models.Model):
    competitor_product_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='product_id')
    platform_id = models.IntegerField()
    platform_product_name = models.CharField(max_length=255, null=True, blank=True)
    platform_product_url = models.TextField(null=True, blank=True)
    sku = models.CharField(max_length=150, null=True, blank=True)
    listed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)
    stock_status = models.CharField(max_length=50, null=True, blank=True)
    delivery_info = models.CharField(max_length=255, null=True, blank=True)
    last_scraped = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "competitor_products"
        managed = False
    def __str__(self):
        return self.platform_product_name or str(self.competitor_product_id)

class ProductMatch(models.Model):
    match_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='product_id')
    competitor_product = models.ForeignKey(CompetitorProduct, on_delete=models.DO_NOTHING, db_column='competitor_product_id')
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    match_status = models.CharField(max_length=20, default='Pending')
    class Meta:
        db_table = "product_matches"
        managed = False
    def __str__(self):
        return f"Match {self.match_id}"

class PricingRecommendation(models.Model):
    recommendation_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(UserProduct, on_delete=models.DO_NOTHING, db_column='user_product_id')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    average_competitor_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lowest_competitor_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    highest_competitor_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    demand_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    inventory_level = models.IntegerField(null=True, blank=True)
    recommended_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_strategy = models.CharField(max_length=100, null=True, blank=True)
    recommendation_reason = models.TextField(null=True, blank=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    parity_price_calc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inventory_price_calc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    demand_price_calc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    class Meta:
        db_table = "pricing_recommendations"
        managed = False
    def __str__(self):
        return f"Rec #{self.recommendation_id}"

class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(UserProduct, on_delete=models.DO_NOTHING, db_column='user_product_id')
    quantity_available = models.IntegerField(null=True, blank=True)
    reorder_level = models.IntegerField(null=True, blank=True)
    warehouse_location = models.CharField(max_length=100, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "inventory"
        managed = False
    def __str__(self):
        return f"Inventory #{self.inventory_id}"

class ProductDemand(models.Model):
    demand_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(UserProduct, on_delete=models.DO_NOTHING, db_column='user_product_id')
    search_count = models.IntegerField(default=0)
    page_views = models.IntegerField(default=0)
    click_count = models.IntegerField(default=0)
    wishlist_count = models.IntegerField(default=0)
    demand_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = "product_demand"
        managed = False
    def __str__(self):
        return f"Demand #{self.demand_id}"