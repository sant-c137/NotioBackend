"""
URL configuration for CourseProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from Notio.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", login_view, name="login"),
    path("api/register/", register_view, name="register"),
    path("api/logout/", logout_view, name="logout"),
    path("api/check_session/", check_session, name="check_session"),
    path("api/get_user_notes/", get_user_notes, name="User notes view"),
    path("api/create_note/", create_note, name="create_note"),
    path("api/delete_note/<int:note_id>/", delete_user_note, name="delete_note"),
    path("api/edit_note/<int:note_id>/", edit_note, name="edit_note"),
    path("api/share_note/", share_note, name="share_note"),
    path("api/get_shared_notes/", get_shared_notes, name="get_shared_notes"),
    path("api/edit_shared_note/<int:note_id>/", edit_shared_note, name="edit_shared_note"),
    
    path('api/user/register/', UserCreate.as_view(), name='user_create'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
    path('accounts/', include('allauth.urls')),
    path('callback/', google_login_callback, name='callback'),
    path('api/auth/user/', UserDetailView.as_view(), name='user_detail'),
    path('api/google/validate_token/', validate_google_token, name='validate_token'),

]
