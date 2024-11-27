'''
from django.urls import path

from . import views

from django.contrib.auth import views as auth_views


urlpatterns = [
    
    path('register', views.register, name='register'),

    path('my-login', views.my_login, name='my-login'),
    path('dashboard', views.dashboard, name='dashboard'),

    path('edit/<int:id>/', views.edit, name='edit'),
    path('delete/<int:id>/', views.delete, name='delete',),



    path('user-logout', views.user_logout, name="user-logout"),
    
#    path('create-thought', views.create_thought, name="create-thought"),
#    path('my-thoughts', views.my_thoughts, name="my-thoughts"),
#    path('update-thought/<str:pk>', views.update_thought, name="update-thought"),
#    path('delete-thought/<str:pk>', views.delete_thought, name="delete-thought"),

    path('profile-management', views.profile_management, name="profile-management"),
    path('delete-account', views.delete_account, name="delete-account"),




    # password management
    # 1- Allow us to enyer our email in order to receive a password reset link
    path('reset_password', auth_views.PasswordResetView.as_view(template_name = "user/password-reset.html"), name = "reset_password" ),

    # 2 showing us a success message stating an email was sent to reset our password
    path('reset_password_sent', auth_views.PasswordResetDoneView.as_view(template_name = "user/password-reset-sent.html"), name="password_reset_done"),

    #3 send a link to our email to reset the password
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = "user/password-reset-form.html"), name ="password_reset_confirm"),

    #4 success message that our password was changed

    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name = "user/password-reset-complete.html"), name = "password_reset_complete"),
    
]
'''

from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('my-login/', views.my_login, name='my-login'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('edit/<str:expense_id>/', views.edit_expense, name='edit'),
    path('delete/<str:expense_id>/', views.delete_expense, name='delete'),
    path('user-logout/', views.user_logout, name='user-logout'),
    path('profile-management/', views.profile_management, name='profile-management'),


    # Password reset views
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

