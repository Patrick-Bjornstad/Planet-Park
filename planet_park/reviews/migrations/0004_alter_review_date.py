# Generated by Django 4.0.3 on 2022-04-15 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_review_image1_alter_review_image2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]