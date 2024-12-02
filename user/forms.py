from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms.widgets import PasswordInput, TextInput




class CreateUserForm(UserCreationForm):
    
    #the form which appears at the registration page.
    
    email = forms.EmailField(required=True)  # to nsure email is required

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']




class LoginForm(AuthenticationForm):
    
    #loginform which appears at the user login page.
    
    username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': 'Password'}))
    
  
  
# expense form during add expense    
class ExpenseForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    category = forms.CharField(max_length=100, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))    


# the user updation form during profile management
class UpdateUserForm(forms.ModelForm):

    password = None

    class Meta:

        model = User
        fields = ['username', 'email',]
        exclude = ['password1', 'password2', ]



#currently profile picture addition is disabled
class UpdateProfileForm(forms.Form):
    """
    Form for updating profile data stored in DynamoDB.
    """
    profile_pic = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
    )


