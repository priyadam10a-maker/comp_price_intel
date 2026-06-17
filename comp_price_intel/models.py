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
    user_product_id = models.AutoField(primary_key=True, db_column='id')
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
    model_number = models.CharField(max_length=150, null=True, blank=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "user_products"
        managed = False
        
    def __str__(self):
        return self.product_name