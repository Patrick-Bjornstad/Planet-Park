from django.db import models

class Activity(models.Model):
    activity_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = 'activities'

    def __str__(self):
        return self.name

class Topic(models.Model):
    topic_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class State(models.Model):
    state_id = models.CharField(max_length=2, primary_key=True)
    state_name = models.CharField(max_length=15)

class Park(models.Model):
    park_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    states = models.ManyToManyField(State)
    latitude = models.FloatField()
    longitude = models.FloatField()
    url = models.URLField()
    address = models.CharField(max_length=100)
    activities = models.ManyToManyField(Activity)
    topics = models.ManyToManyField(Topic)
    description = models.TextField()
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    min_price = models.FloatField()
    max_price = models.FloatField()

    def __str__(self):
        return self.name
