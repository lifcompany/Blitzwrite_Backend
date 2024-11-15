from rest_framework import serializers
from .models import Keyword, SuggestedKeyword, Notification, Article

class SuggestKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestedKeyword
        fields = ['main_keyword', 'keyword', 'volume']

    def create(self, validated_data):
        main_keyword = validated_data.pop('main_keyword')
        keyword_instance = SuggestedKeyword.objects.create(main_keyword=main_keyword, **validated_data)
        return keyword_instance
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'content', 'read', 'timestamp']
        
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'user', 'title', 'site_url', 'keywords', 'wp_status', 'category', 'current_clicks', 'last_month_clicks', 'created_at']