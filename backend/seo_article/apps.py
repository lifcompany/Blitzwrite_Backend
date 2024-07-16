from django.apps import AppConfig


class SeoArticleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'seo_article'
    def ready(self):
        import seo_article.signals