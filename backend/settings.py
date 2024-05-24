# settings.py

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OPENAI_API_KEY='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'
# Other settings ...

# Add this line to set the directory where files are stored
FILES_DIRECTORY = os.path.join(BASE_DIR, 'files')
# Stripe API keys
STRIPE_SECRET_KEY = 'stripe_test_key'
STRIPE_PUBLIC_KEY = 'stripe_public_key'
STRIPE_SECRET_KEY = 'stripe_secret_key'

# CORS settings (for local development)
CORS_ORIGIN_ALLOW_ALL = True  # Allow requests from all origins (for testing)
