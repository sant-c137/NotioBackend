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
from django.urls import path
from Notio.views import (
    get_user_notes,
    login_view,
    register_view,
    check_session,
    logout_view,
    create_note,
    delete_user_note,
    edit_note,
    share_note,
    get_shared_notes
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login/", login_view, name="login"),
    path("api/logout/", logout_view, name="logout"),
    path("api/register/", register_view, name="register"),
    path("api/check_session/", check_session, name="check_session"),
    path("api/get_user_notes/", get_user_notes, name="User notes view"),
    path("api/create_note/", create_note, name="create_note"),
    path("api/delete_note/<int:note_id>/", delete_user_note, name="delete_note"),
    path("api/edit_note/<int:note_id>/", edit_note, name="edit_note"),
    path("api/share_note/", share_note, name="share_note"),
    path("api/get_shared_notes/", get_shared_notes, name="get_shared_notes"),

]
