from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from authentication import views

urlpatterns=[
    path('register/',views.Registration,name='register'),
    path('login/',views.Login,name='login'),
    path('logout/',views.Logout,name='logout'),
    path('validation-username/',csrf_exempt(views.username_validation),name='validation-username'),
    path('validation-password/',csrf_exempt(views.password_validation),name='validation-password'),
    path('validation-email/',csrf_exempt(views.email_validation),name='validation-email'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('reset-password/', views.ResetPassword, name='reset-password'),
    path('setnew-password/<str:uidb64>/<str:token>', views.set_password, name='set-password'),
  
]