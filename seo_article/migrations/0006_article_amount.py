# Generated by Django 4.2.10 on 2024-08-16 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo_article', '0005_alter_article_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
