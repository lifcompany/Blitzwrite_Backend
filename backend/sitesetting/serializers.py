# serializers.py
from rest_framework import serializers
from .models import SiteData, LifVersion

class SiteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteData
        fields = ['site_name', 'site_url', 'admin_name', 'admin_pass']

class LifVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifVersion
        fields = '__all__'