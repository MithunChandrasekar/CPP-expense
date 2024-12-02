'''
from django.db import models
from django.contrib.auth.models import User

class Thought(models.Model):
    title = models.CharField(max_length=150)
    content = models.CharField(max_length=400)
    date = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, max_length=10, on_delete=models.CASCADE, null = True)
'''

'''    

class Profile(models.Model):
    profile_pic = models.ImageField(null=True, blank = True, default = 'Default.png')
    user = models.ForeignKey(User, max_length=10, on_delete=models.CASCADE, null = True)

class Expense(models.Model):
    name = models.CharField(max_length = 100)
    amount = models.IntegerField()
    category = models.CharField(max_length=50)
    date = models.DateField(auto_now=True)
    user = models.ForeignKey(User, max_length=10, on_delete=models.CASCADE, null = True)
'''
import boto3
# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# DynamoDB Tables
profile_table = dynamodb.Table('Profile')
expense_table = dynamodb.Table('Expense')


#django model to get the profile picture currently disabled
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)  # Replace 1 with a valid user ID
    picture = models.ImageField(upload_to='profile_pictures/', default='default.png')


# class which contains aws sdk code to dynamo db for user management
class ProfileManager:
    @staticmethod
    def create_profile(user_id, profile_pic='Default.png'):
        profile_table.put_item(
            Item={
                'user_id': user_id,
                'profile_pic': profile_pic,
            }
        )

    @staticmethod
    def get_profile(user_id):
        response = profile_table.get_item(Key={'user_id': user_id})
        return response.get('Item')

    @staticmethod
    def update_profile(user_id, profile_pic):
        profile_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression="set profile_pic = :p",
            ExpressionAttributeValues={':p': profile_pic},
        )

    @staticmethod
    def delete_profile(user_id):
        profile_table.delete_item(Key={'user_id': user_id})

# class which contains aws sdk code to dynamo db for expense management
class ExpenseManager:
    @staticmethod
    def create_expense(expense_id, user_id, name, amount, category, date):
        expense_table.put_item(
            Item={
                'expense_id': expense_id,
                'user_id': user_id,
                'name': name,
                'amount': amount,
                'category': category,
                'date': date,
            }
        )
    @staticmethod
    def get_expenses_by_user(user_id):
        try:
            response = expense_table.scan(
                FilterExpression="user_id = :uid",
                ExpressionAttributeValues={':uid': user_id}
            )
            return response.get('Items', [])
        except Exception as e:
            #logger.error(f"Error fetching expenses for user {user_id}: {e}")
            return []


    @staticmethod
    def update_expense(expense_id, user_id, **kwargs):
        # used to not allow the user to add any detail same as the keywords in AWS
        update_expression = "SET " + ", ".join(f"#{k} = :{k}" for k in kwargs)
        expression_attribute_names = {f"#{k}": k for k in kwargs}
        expression_values = {f":{k}": v for k, v in kwargs.items()}
    
        expense_table.update_item(
            Key={'expense_id': expense_id, 'user_id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_values,
        )

    @staticmethod
    def delete_expense(expense_id, user_id):
        expense_table.delete_item(Key={'expense_id': expense_id, 'user_id': user_id})
