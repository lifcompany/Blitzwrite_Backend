from rest_framework import serializers
from .models import Keyword, SuggestedKeyword

class SuggestKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestedKeyword
        fields = ['main_keyword', 'keyword', 'volume']

    def create(self, validated_data):
        main_keyword = validated_data.pop('main_keyword')
        keyword_instance = SuggestedKeyword.objects.create(main_keyword=main_keyword, **validated_data)
        return keyword_instance
        