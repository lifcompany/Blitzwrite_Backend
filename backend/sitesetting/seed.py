# seed_data.py

from django.core.management.base import BaseCommand
from .models import LifVersion  # Import your model here

class Command(BaseCommand):
    help = 'Seed initial data'

    def handle(self, *args, **kwargs):
        LifVersion.objects.bulk_create([
            LifVersion(display_name="GPT-4", model_name="gpt-4", endpoint="https://api.openai.com/v1/chat/completions", params=""),
            LifVersion(display_name="GPT-4-turbo", model_name="gpt-4-turbo", endpoint="https://api.openai.com/v1/chat/completions", params=""),
            LifVersion(display_name="GPT-4-1106-Preview", model_name="gpt-4-1106-preview", endpoint="https://api.openai.com/v1/chat/completions", params=""),
            LifVersion(display_name="GPT-4-Turbo-Preview", model_name="gpt-4-turbo-preview", endpoint="https://api.openai.com/v1/chat/completions", params=""),
            LifVersion(display_name="GPT-3.5-Turbo-0125", model_name="gpt-3.5-turbo-0125", endpoint="https://api.openai.com/v1/chat/completions", params=""),
            LifVersion(display_name="GPT-3.5-Turbo-Instruct", model_name="gpt-3.5-turbo-instruct", endpoint="https://api.openai.com/v1/completions", params=""),
        ])
        self.stdout.write(self.style.SUCCESS('Data seeded successfully.'))
