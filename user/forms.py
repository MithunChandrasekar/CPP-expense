from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput




class CreateUserForm(UserCreationForm):
    """
    Form for creating new users. Extends the built-in UserCreationForm.
    """
    email = forms.EmailField(required=True)  # Ensure email is required

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']




class LoginForm(AuthenticationForm):
    """
    Custom login form with additional styling or customization.
    """
    username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Password'}))

'''

class ExpenceForm(forms.Form):
    """
    Form for creating and managing expenses in DynamoDB.
    """
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Expense Name'}),
    )
    amount = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Amount'}),
    )
    category = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Category'}),
    )
'''
    
class ExpenseForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    category = forms.ChoiceField(
        choices=[
            ('entertainment', 'Entertainment'),
            ('grocery', 'Transport'),
            ('leisure', 'Leisure'),
            ('rent+bills', 'Rent+Bills'),
            ('transportation', 'Transportation'),
            ('other', 'Other'),
        ],
        required=True
    )
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))    



class UpdateUserForm(forms.ModelForm):

    password = None

    class Meta:

        model = User
        fields = ['username', 'email',]
        exclude = ['password1', 'password2', ]




class UpdateProfileForm(forms.Form):
    """
    Form for updating profile data stored in DynamoDB.
    """
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
    )


