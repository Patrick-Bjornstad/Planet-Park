from django.urls import path

from .views import discover, info_page

urlpatterns = [
    path('', discover, name='discover'),
    path('<str:park_code>', info_page, name='info_page')
]
