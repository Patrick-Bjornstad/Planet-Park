from django.forms import ModelForm, ImageField

from reviews.models import Review

class ReviewForm(ModelForm):
    image1 = ImageField(required=False)
    image2 = ImageField(required=False)
    image3 = ImageField(required=False)

    class Meta:
        model = Review
        exclude = ['author', 'date']
