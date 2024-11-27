from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import ProfileManager, ExpenseManager
from .forms import CreateUserForm, LoginForm, ExpenceForm, UpdateProfileForm, UpdateUserForm
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

def homepage(request):
    # Log a test message
    #logger.info("Homepage accessed")
    return render(request, 'user/index.html')






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
                    'profile_pic_url': f"{settings.MEDIA_URL}profile_pictures/default.png"  # Default profile picture
                }
            )

            return redirect('my-login')  # Redirect to login page after successful registration
    else:
        
        form = CreateUserForm()
    
    return render(request, 'user/register.html', {'form': form})






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



@login_required(login_url='my-login')
def user_logout(request):
    logout(request)
    return redirect("")




def get_profile_picture(user_id):
    """
    Fetch the profile picture URL from DynamoDB or return the default picture URL.
    """
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_S3_REGION_NAME)
    profile_table = dynamodb.Table('Profile')

    response = profile_table.get_item(Key={'user_id': user_id})
    if 'Item' in response and 'profile_pic_url' in response['Item']:
        return response['Item']['profile_pic_url']
    
    # Return default picture URL
    return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/profile_pictures/default.png"



@login_required(login_url='my-login')
def dashboard(request):
    user_id = str(request.user.id)
    profile_pic_url = get_profile_picture(user_id)
    
    if request.method == 'POST':
        form = ExpenceForm(request.POST)
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
        form = ExpenceForm()

    # Fetch existing expenses
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
        expense_date = expense.get('date')  # Assuming 'date' is in 'YYYY-MM-DD' format
        if expense_date and expense_date >= thirty_days_ago.isoformat():
            daily_sums[expense_date] += float(expense.get('amount', 0))  # Convert amount to float

    # Sort daily sums by date
    daily_sums_sorted = sorted(daily_sums.items(), key=lambda x: x[0])

    # Calculate expenses based on categories
       
    categorical_sums = defaultdict(float)
    for expense in expenses:
        category = expense.get('category', 'Uncategorized')
        amount = float(expense.get('amount', 0))  # Convert to float
        categorical_sums[category] += amount

  
    

    context = {
        'profilePic': profile_pic_url,
        'username': request.user.username,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'yearly_sum': yearly_expenses,
        'monthly_sum': monthly_expenses,
        'weekly_sum': weekly_expenses,
        'daily_sums': daily_sums_sorted,  # Pass daily expenses for 30 days
        'categorical_sums': dict(categorical_sums),  # Pass category-based sums
        'form': form,
    }
    return render(request, 'user/dashboard.html', context)





@login_required(login_url='my-login')
def add_expense(request):
    if request.method == 'POST':
        form = ExpenceForm(request.POST)
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

    form = ExpenceForm()
    return render(request, 'user/add-expense.html', {'form': form})

'''

@login_required(login_url='my-login')
def edit_expense(request, expense_id):
    user_id = str(request.user.id)
    if request.method == 'POST':
        form = ExpenceForm(request.POST)
        if form.is_valid():
            expense_data = form.cleaned_data
            ExpenseManager.update_expense(
                expense_id=expense_id,
                user_id=user_id,
                name=expense_data['name'],
                amount=expense_data['amount'],
                category=expense_data['category']
            )
            return redirect('dashboard')

    # Pre-fill the form with existing data (fetch from DynamoDB)
    expenses = ExpenseManager.get_expenses_by_user(user_id)
    expense = next((exp for exp in expenses if exp['expense_id'] == expense_id), None)
    form = ExpenceForm(initial=expense)
    return render(request, 'user/edit-expense.html', {'form': form})
'''

@login_required(login_url='my-login')
def edit_expense(request, expense_id):
    user_id = str(request.user.id)

    # Fetch the specific expense from DynamoDB
    expenses = ExpenseManager.get_expenses_by_user(user_id)
    expense = next((exp for exp in expenses if exp['expense_id'] == expense_id), None)

    if not expense:
        messages.error(request, "Expense not found.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ExpenceForm(request.POST)
        if form.is_valid():
            ExpenseManager.update_expense(
                expense_id=expense_id,
                user_id=user_id,
                name=form.cleaned_data['name'],
                category=form.cleaned_data['category'],  # No predefined category constraints
                amount=form.cleaned_data['amount']
            )
            messages.success(request, "Expense updated successfully.")
            return redirect('dashboard')

    # Pre-fill the form with existing expense data
    form = ExpenceForm(initial=expense)

    return render(request, 'user/edit-expense.html', {'form': form})


@login_required(login_url='my-login')
def delete_expense(request, expense_id):
    if request.method == 'POST':
        ExpenseManager.delete_expense(expense_id=expense_id, user_id=str(request.user.id))
        return redirect('dashboard')
    return render(request, 'user/delete-expense.html')





'''
@login_required(login_url='my-login')
def update_profile(request):
    """
    Handles profile updates, including profile picture uploads to S3.
    """
    user_id = str(request.user.id)
    dynamodb = boto3.resource('dynamodb', region_name=settings.AWS_S3_REGION_NAME)
    s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)

    # Fetch user profile from DynamoDB
    profile_table = dynamodb.Table('Profiles')  # Replace 'Profiles' with your actual table name
    profile_data = profile_table.get_item(Key={'user_id': user_id}).get('Item', {})

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle profile picture upload
            profile_pic = request.FILES.get('profile_pic', None)
            if profile_pic:
                # Upload to S3
                s3_key = f"profile_pictures/{user_id}/{profile_pic.name}"
                s3_client.upload_fileobj(
                    profile_pic,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    s3_key,
                    ExtraArgs={'ACL': 'public-read'}  # Public-read, adjust if needed
                )
                # Update S3 URL in DynamoDB
                profile_pic_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
                profile_table.update_item(
                    Key={'user_id': user_id},
                    UpdateExpression="SET profile_pic_url = :url",
                    ExpressionAttributeValues={':url': profile_pic_url}
                )

            # Update other profile details in DynamoDB
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            profile_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression="SET username = :username, email = :email",
                ExpressionAttributeValues={
                    ':username': username,
                    ':email': email,
                }
            )
            return redirect('dashboard')

    # Populate the form with data from DynamoDB
    initial_data = {
        'username': profile_data.get('username', ''),
        'email': profile_data.get('email', ''),
    }
    form = UpdateProfileForm(initial=initial_data)
    return render(request, 'user/update-profile.html', {'form': form})
'''





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

    # Default profile picture if no record is found
    if not profile_data:
        profile_data = {
            'user_id': user_id,
            'username': request.user.username,
            'email': request.user.email,
            'profile_pic_url': f"https://{bucket_name}.s3.{region}.amazonaws.com/profile_pictures/default.png",
        }

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES)

        # Check both forms for validity
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

                # Handle profile picture upload
                profile_pic = profile_form.cleaned_data.get('profile_pic')
                if profile_pic:
                    try:
                        s3_client = boto3.client('s3', region_name=region)
                        s3_client.upload_fileobj(
                            profile_pic,
                            bucket_name,
                            f"profile_pictures/{user_id}.png"
                        )
                        # Generate a pre-signed URL to access the file privately
                        presigned_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={
                                'Bucket': bucket_name,
                                'Key': f"profile_pictures/{user_id}.png"
                            },
                            ExpiresIn=3600  # URL expiration time in seconds
                        )
                        profile_data['profile_pic_url'] = presigned_url
                        #logger.info("Profile picture uploaded successfully to S3.")
                    except Exception as s3_error:
                        #logger.error(f"Error uploading profile picture to S3: {s3_error}")
                        profile_data['profile_pic_url'] = f"https://{bucket_name}.s3.{region}.amazonaws.com/profile_pictures/default.png"

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
                        f"Profile Picture: {profile_data['profile_pic_url']}"
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




@login_required(login_url='my-login')
def delete_account(request):
    user = request.user

    # Handle account deletion
    if request.method == 'POST':
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('my-login')  # Redirect to login page or home page after deletion

    return render(request, 'user/delete-account.html')