from django.urls import path
from user import views

#user/create -> register new user
#user/token -> create a new token
#user/me -> update profile, OR view profile

app_name = 'user'

urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token' ),
    path('me/', views.ManageUserView.as_view(), name='me' ),
]
