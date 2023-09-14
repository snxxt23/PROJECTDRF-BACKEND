from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('registration/',views.UserRegistration.as_view(),name='registration'),
    path('login/',views.MyTokenObtainPairView.as_view(),name='login'),
    path('refresh/',views.TokenObtainPairView.as_view(),name='refresh'),
    path('profile/',views.UserProfile.as_view(),name='refresh'),
    path('userprofile/',views.UserProfileView.as_view(),name='userprofile'),
    path('userprofile/<int:pk>/',views.UserProfileView.as_view(),name='userprofileedit'),
    path('doctor/',views.UserDoctorView.as_view(),name='doctor'),
    

]