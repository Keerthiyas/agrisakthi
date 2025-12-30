import os
import sys
import django

# 🔹 Add project root to PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 🔹 Point to Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()

from crop.models import Scheme
from django.utils.text import slugify

for s in Scheme.objects.all():
    if not s.slug:
        s.slug = slugify(f"{s.name}-{s.id}")
        s.save()

print("All empty slugs fixed!")
