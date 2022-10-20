from django.urls import path

from .views import review_general, review_specific, reviews_list

urlpatterns = [
    path('', reviews_list, name='reviews_list'),
    path('create/', review_general, name='review_general'),
    path('create/<str:park_code>', review_specific, name='review_specific')
]
