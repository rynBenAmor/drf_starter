from django.urls import path
from .views import (UserInfoView,
                     UserRegistrationView,
                       UserLoginView,
                         UserLogoutView,
                         CookieTokenRefreshView)



urlpatterns = [
    path('me/', UserInfoView.as_view(), name='user-info'),    
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token-refresh'),

]