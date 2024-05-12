from tortoise.models import Model
from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator

class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    quantity_stock = fields.IntField(default=0)
    quantity_sold = fields.IntField(default=0)
    unit_price = fields.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    revenue = fields.DecimalField(max_digits=20, decimal_places=2, default=0.0)
    supplied_by = fields.ForeignKeyField('models.User', related_name='goods_supplied')

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100)
    phone = fields.CharField(max_length=20)
    company = fields.CharField(max_length=100)

# Create Pydantic models
Product_Pydantic = pydantic_model_creator(Product, name="Product")
Product_PydanticIn = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)

user_Pydantic = pydantic_model_creator(User, name="User")
user_PydanticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)