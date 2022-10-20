"""planet_park URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

from discovery.dashapps import discover_table

urlpatterns = [
    # Django-plotly-dash required url
    path('django_plotly_dash/', include('django_plotly_dash.urls')),

    # Admin page url
    path('admin/', admin.site.urls),

    # App urls
    path('', include('home.urls')),
    path('discovery/', include('discovery.urls')),
    path('reviews/', include('reviews.urls'))
]
