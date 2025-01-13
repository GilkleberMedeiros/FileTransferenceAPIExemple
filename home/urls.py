"""
URL configuration for home project.

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
from django.contrib import admin  # type: ignore
from django.urls import path  # type: ignore

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from FTAPI.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("files/", ListCreateFilesView.as_view(), name="ListCreateFiles"),
    path("files/<int:file_id>/", DetailDelFilesView.as_view(), name="DetailDelFiles"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc_docs"),
]
