'''

from django.shortcuts import render, redirect
from . forms import CreateUserForm, LoginForm, UpdateUserForm, UpdateProfileForm, ExpenceForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from . models import Profile, Expense

from django.core.mail import send_mail
from django.conf import settings

# Create your views here.
import datetime
from django.db.models import Sum







def homepage(request):
    return render(request, 'user/index.html')




def register(request):
    
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            current_user = form.save(commit=False)
            form.save()

            send_mail("Welcome to TrackYourEuro", "All the best to track and Save ur leaking euros", settings.DEFAULT_FROM_EMAIL, [current_user.email])
            profile = Profile.objects.create(user=current_user)
            
            messages.success(request, "User created!")
            return redirect ('my-login')

    
    context = {'RegistrationForm': form}
    return render(request, 'user/register.html', context)





def my_login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('dashboard')
            
    context = {'LoginForm' : form}
    return render(request, 'user/my-login.html', context)





def user_logout(request):
    auth.logout(request)
    
    return redirect("")



'''
'''
@login_required(login_url='my-login')
def dashboard(request):
    profile_pic = Profile.objects.get(user= request.user)
    context = {'profilePic' : profile_pic}

    return render(request, 'user/dashboard.html', context)

'''
'''


@login_required(login_url='my-login')
def dashboard(request):


    profile_pic = Profile.objects.get(user= request.user)

    if request.method == "POST":
        expense = ExpenceForm(request.POST)
        if expense.is_valid():
            expitem = expense.save(commit = False)
            expitem.user = request.user
            expitem.save()

  
    #total in the chart
    current_user = request.user.id
    user_expenses = Expense.objects.all().filter(user = current_user)
    total_expenses = user_expenses.aggregate(Sum('amount'))


    #calculate 1 year's exp
    last_year = datetime.date.today() - datetime.timedelta(days=365)
    data = Expense.objects.filter(date__gt=last_year)
    user_data = data.filter(user = current_user)
    yearly_sum = user_data.aggregate(Sum('amount'))


    #calculate 1 month's exp
    last_month = datetime.date.today() - datetime.timedelta(days=30)
    month_data = Expense.objects.filter(date__gt=last_month)
    user_month_data = month_data.filter(user = current_user)
    monthly_sum = user_month_data.aggregate(Sum('amount'))


    #calculate 1 week's exp
    last_week = datetime.date.today() - datetime.timedelta(days=7)
    weekly_data = Expense.objects.filter(date__gt=last_week)
    user_weekly_data = weekly_data.filter(user = current_user)
    weekly_sum = user_weekly_data.aggregate(Sum('amount'))


    daily_sums = Expense.objects.filter(user = current_user).values('date').order_by('date').annotate(sum=Sum('amount'))


    Categorical_sums = Expense.objects.filter(user = current_user).values('category').order_by('date').annotate(sum=Sum('amount'))


    expense_form = ExpenceForm()
    context = {'profilePic' : profile_pic, 'expense_form' : expense_form, 'expenses': user_expenses, 'total_expenses':total_expenses, 'yearly_sum': yearly_sum, 'monthly_sum': monthly_sum, 'weekly_sum' : weekly_sum, 'daily_sums': daily_sums, 'Categorical_sums' : Categorical_sums }
    return render(request, 'user/dashboard.html', context)




@login_required(login_url='my-login')
def edit(request, id):
    expense = Expense.objects.get(id=id)
    expense_form = ExpenceForm(instance=expense)
    if request.method =="POST":
        expense = Expense.objects.get(id=id)
        form = ExpenceForm(request.POST, instance = expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')

    context = {'expense_form': expense_form}
    return render(request, 'user/edit.html', context)







def delete(request, id):
    if request.method =='POST' and 'delete' in request.POST:
        expense =Expense.objects.get(id=id)
        expense.delete()

    return redirect('dashboard')



'''
'''
def create_thought(request):
    form = ThoughtForm()
    if request.method == 'POST':
        form = ThoughtForm(request.POST)

        if form.is_valid():
            thought = form.save(commit = False)
            thought.user = request.user
            thought.save()

            return redirect ('my-thoughts')

    context = {'CreateThoughtForm' : form} 
'''
  


'''

@login_required(login_url ='my-login')
def create_thought(request):
    form = ThoughtForm()
    if request.method == 'POST':
        form = ThoughtForm(request.POST)

        if form.is_valid():
            thought = form.save(commit = False)
            thought.user = request.user
            thought.save()

            return redirect ('my-thoughts')

    context = {'CreateThoughtForm' : form}
    return render(request, 'user/create-thought.html' , context)





@login_required(login_url ='my-login')
def my_thoughts(request):
    current_user = request.user.id
    thought = Thought.objects.all().filter(user = current_user)

    context = {'AllThoughts': thought}

    return render(request, 'user/my-thoughts.html', context)





@login_required(login_url ='my-login')
def update_thought(request, pk):

    try: 
        thought = Thought.objects.get(id=pk, user = request.user)
    except:
        return redirect('my-thoughts')


    thought = Thought.objects.get(id=pk, user = request.user)
    form = ThoughtForm(instance=thought)

    if request.method == 'POST':
        form = ThoughtForm(request.POST, instance=thought)

        if form.is_valid():
            form.save()
            return redirect('my-thoughts')
    context = {'UpdateThought' : form}  

    
    return render(request, 'user/update-thought.html', context)





@login_required(login_url ='my-login')
def delete_thought(request, pk):

    try: 
        thought = Thought.objects.get(id=pk, user = request.user)
    except:
        return redirect('my-thoughts')

    if request.method =="POST":

        thought.delete()
        return redirect('my-thoughts')
    
    return render(request, 'user/delete-thought.html')
'''

'''

@login_required(login_url ='my-login')
def profile_management(request):
    form = UpdateUserForm( instance= request.user)

    profile = Profile.objects.get(user = request.user)
    form_2 = UpdateProfileForm(instance=profile)



    if request.method =="POST":
        form = UpdateUserForm(request.POST, instance = request.user)
        form_2 = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')    
        
        if form_2.is_valid():
            form_2.save()
            return redirect('dashboard')

    context = {'UserUpdateForm': form, 'ProfileUpdateForm': form_2}

    return render(request, 'user/profile-management.html', context)





@login_required(login_url ='my-login')
def delete_account(request):
    
    if request.method == 'POST':
        deleteUser = User.objects.get(username=request.user)
        deleteUser.delete() 
        return redirect("")

    return render(request, 'user/delete-account.html')


'''

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

'''
def register(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            current_user = form.save(commit=False)
            form.save()
            # Create profile in DynamoDB
            ProfileManager.create_profile(str(current_user.id))
            messages.success(request, "User created!")
            return redirect('my-login')

    context = {'RegistrationForm': form}
    return render(request, 'user/register.html', context)
'''

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


@login_required(login_url='my-login')
def delete_expense(request, expense_id):
    if request.method == 'POST':
        ExpenseManager.delete_expense(expense_id=expense_id, user_id=str(request.user.id))
        return redirect('dashboard')
    return render(request, 'user/delete-expense.html')






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
                        logger.info("Profile picture uploaded successfully to S3.")
                    except Exception as s3_error:
                        logger.error(f"Error uploading profile picture to S3: {s3_error}")
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
                    logger.info("SNS notification sent successfully.")
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