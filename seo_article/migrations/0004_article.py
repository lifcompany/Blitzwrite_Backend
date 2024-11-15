# Generated by Django 4.2.10 on 2024-08-16 15:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('seo_article', '0003_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('keywords', models.TextField()),
                ('wp_status', models.CharField(choices=[('public', 'Public'), ('draft', 'Draft')], max_length=10)),
                ('category', models.CharField(blank=True, max_length=255, null=True)),
                ('current_clicks', models.IntegerField(default=0)),
                ('last_month_clicks', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
