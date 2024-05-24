# Generated by Django 4.2.10 on 2024-05-24 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sitesetting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(max_length=255)),
                ('site_url', models.URLField()),
                ('admin_name', models.CharField(max_length=255)),
                ('admin_pass', models.CharField(max_length=255)),
            ],
        ),
    ]