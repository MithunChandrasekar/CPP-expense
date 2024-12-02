from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import ProfileManager, ExpenseManager, expense_table
from .forms import CreateUserForm, LoginForm, ExpenseForm, UpdateProfileForm, UpdateUserForm
import uuid  # For generating unique expense IDs
import datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from django.conf import settings
from django.contrib.auth.models import User
import boto3


'''
import logging
logger = logging.getLogger(__name__)
'''
import logging
logger = logging.getLogger(__name__)

# landing page of the user
def homepage(request):
    
    return render(request, 'user/index.html')





# registration page 
def register(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            # Save the user to the Django User model
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()

            # Add the user profile to DynamoDB with default profile picture
            dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_S3_REGION_NAME)
            profile_table = dynamodb.Table('Profile')

            profile_table.put_item(
                Item={
                    'user_id': str(user.id),  # DynamoDB uses user_id as the partition key
                    'username': user.username,
                    'email': user.email,
                }
            )

            return redirect('my-login')  # Redirect to login page after successful registration
    else:
        
        form = CreateUserForm()
    
    return render(request, 'user/register.html', {'form': form})





#Login page
def my_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to dashboard after login
    context = {'LoginForm': form}
    return render(request, 'user/my-login.html', context)


# logout button
@login_required(login_url='my-login')
def user_logout(request):
    logout(request)
    return redirect('homepage')


# user landing page after authentication
@login_required(login_url='my-login')
def dashboard(request):
    user_id = str(request.user.id)
    
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense_data = form.cleaned_data
            expense_id = str(uuid.uuid4())  # Generate unique ID
            ExpenseManager.create_expense(
                expense_id=expense_id,
                user_id=user_id,
                name=expense_data['name'],
                amount=expense_data['amount'],
                category=expense_data['category'],
                date=datetime.date.today().isoformat(),
            )
            return redirect('dashboard')  # Refresh the page to display updated data
    else:
        form = ExpenseForm()

    # Read operation on the expense 
    expenses = ExpenseManager.get_expenses_by_user(user_id)

    # Calculate total expenses
    total_expenses = sum(expense['amount'] for expense in expenses if 'amount' in expense)

    # Calculate date ranges
    today = datetime.date.today()
    one_year_ago = today - relativedelta(years=1)
    one_month_ago = today - relativedelta(months=1)
    one_week_ago = today - datetime.timedelta(weeks=1)

    # Filter expenses for the last year, month, and week
    yearly_expenses = sum(expense['amount'] for expense in expenses if 'amount' in expense and expense['date'] >= one_year_ago.isoformat())
    monthly_expenses = sum(expense['amount'] for expense in expenses if 'amount' in expense and expense['date'] >= one_month_ago.isoformat())
    weekly_expenses = sum(expense['amount'] for expense in expenses if 'amount' in expense and expense['date'] >= one_week_ago.isoformat())
    
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    daily_sums = defaultdict(float)
    for expense in expenses:
        expense_date = expense.get('date')  
        if expense_date and expense_date >= thirty_days_ago.isoformat():
            daily_sums[expense_date] += float(expense.get('amount', 0))  

    # Sort daily sums by date
    daily_sums_sorted = sorted(daily_sums.items(), key=lambda x: x[0])

    # Calculate expenses based on categories
       
    categorical_sums = defaultdict(float)
    for expense in expenses:
        category = expense.get('category', 'Uncategorized')
        amount = float(expense.get('amount', 0))  # Convert to float
        categorical_sums[category] += amount

  
    

    context = {
        
        'username': request.user.username,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'yearly_sum': yearly_expenses,
        'monthly_sum': monthly_expenses,
        'weekly_sum': weekly_expenses,
        'daily_sums': daily_sums_sorted,  # Pass daily expenses for 30 days
        'categorical_sums': dict(categorical_sums),  # Pass category-based sums for the chart JS
        'form': form,
    }
    return render(request, 'user/dashboard.html', context)



# used to create the expense

@login_required(login_url='my-login')
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense_data = form.cleaned_data
            expense_id = str(uuid.uuid4())  # Generate unique ID
            ExpenseManager.create_expense(
                expense_id=expense_id,
                user_id=str(request.user.id),
                name=expense_data['name'],
                amount=expense_data['amount'],
                category=expense_data['category'],
                date=datetime.date.today().isoformat(),
            )
            return redirect('dashboard')

    form = ExpenseForm()
    return render(request, 'user/add-expense.html', {'form': form})




#used to update the expense

@login_required(login_url='my-login')
def edit_expense(request, expense_id):
    # Get the current user ID
    user_id = str(request.user.id)
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Replace with your AWS region

    # Fetch the expense details from DynamoDB
    expenses = ExpenseManager.get_expenses_by_user(user_id)
    expense = next((item for item in expenses if item['expense_id'] == expense_id), None)

    if not expense:
        return redirect('dashboard')  # Redirect if the expense doesn't exist

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense_data = form.cleaned_data
            ExpenseManager.update_expense(
                expense_id=expense_id,
                user_id=user_id,
                name=expense_data['name'],
                amount=expense_data['amount'],
                category=expense_data['category'],
                date=expense_data['date'].isoformat(),  # Convert date to string
            )
            
            return redirect('dashboard')
    
    else:
        # Populate the form with the current expense data
        form = ExpenseForm(initial={
            'name': expense['name'],
            'amount': expense['amount'],
            'category': expense['category'],
            'date': expense['date'],
        })

    return render(request, 'user/edit-expense.html', {'form': form})


# Used to delete the expense
@login_required(login_url='my-login')
def delete_expense(request, expense_id):
    if request.method == 'POST':
        ExpenseManager.delete_expense(expense_id=expense_id, user_id=str(request.user.id))
        return redirect('dashboard')
    return render(request, 'user/delete-expense.html')




# Set up logging for debugging
#logger = logging.getLogger(__name__)

@login_required(login_url='my-login')
def profile_management(request):
    user_id = str(request.user.id)  # Get user ID from the logged-in user
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Replace with your AWS region
    profile_table = dynamodb.Table('Profile')

    bucket_name = 'my-expense-app-bucket'  # Replace with your actual bucket name
    region = 'us-east-1'  # Replace with your actual region

    # Fetch existing data from DynamoDB
    try:
        profile_data = profile_table.get_item(Key={'user_id': user_id}).get('Item', {})
    except Exception as e:
        profile_data = {}
        #logger.error(f"Error fetching profile data from DynamoDB: {e}")

    if not profile_data:
        profile_data = {
            'user_id': user_id,
            'username': request.user.username,
            'email': request.user.email,
        }

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                # Update user model data
                user = user_form.save(commit=False)
                user.username = user_form.cleaned_data.get('username')
                user.email = user_form.cleaned_data.get('email')
                user.save()

                # Update DynamoDB profile data
                profile_data['username'] = user.username
                profile_data['email'] = user.email
                
                # Save updated profile data to DynamoDB
                profile_table.put_item(Item=profile_data)

                # SNS Notification
                try:
                    sns_client = boto3.client('sns', region_name=region)
                    sns_topic_arn = 'arn:aws:sns:us-east-1:973195829891:user-notifications'  # Replace with your SNS Topic ARN
                    sns_message = (
                        f"Profile updated successfully!\n\n"
                        f"Username: {user.username}\n"
                        f"Email: {user.email}\n"
                    )
                    sns_client.publish(
                        TopicArn=sns_topic_arn,
                        Message=sns_message,
                        Subject="Profile Update Notification"
                    )
                    #logger.info("SNS notification sent successfully.")
                except Exception as sns_error:
                    logger.error(f"Error sending SNS notification: {sns_error}")

                return redirect('dashboard')
            except Exception as e:
                logger.error(f"Error updating profile: {e}")
    else:
        # Populate forms with initial data
        user_form = UpdateUserForm(initial={
            'username': profile_data.get('username', ''),
            'email': profile_data.get('email', ''),
        })
        profile_form = UpdateProfileForm()

    return render(request, 'user/profile-management.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_pic_url': profile_data.get('profile_pic_url'),
    })



# delete the account from profile management page
@login_required(login_url='my-login')
def delete_account(request):
    user = request.user

    # Handle account deletion
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('my-login')  # Redirect to login page or home page after deletion

    return render(request, 'user/delete-account.html')