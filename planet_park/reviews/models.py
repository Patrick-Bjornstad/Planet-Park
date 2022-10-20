from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from cloudinary.models import CloudinaryField

from django.contrib.auth.models import User

from discovery.models import Park

class Review(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    park = models.ForeignKey(Park, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text='Min rating: 0, max rating: 5',
        default=5
    )
    body = models.TextField()
    image1 = CloudinaryField('image', null=True, blank=True)
    image2 = CloudinaryField('image', null=True, blank=True)
    image3 = CloudinaryField('image', null=True, blank=True)

    class Meta:
        get_latest_by = 'date'
        ordering = ('-date',)
        constraints = (
            models.CheckConstraint(
                check=models.Q(rating__gte=0) & models.Q(rating__lte=5),
                name='rating_range'
            ),
        )
    