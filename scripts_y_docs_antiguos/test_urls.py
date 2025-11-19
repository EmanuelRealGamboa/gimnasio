import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')
django.setup()

from django.urls import get_resolver

resolver = get_resolver()

print("URLs que contienen 'acceso':")
for pattern in resolver.url_patterns:
    try:
        if hasattr(pattern, 'url_patterns'):
            for sub_pattern in pattern.url_patterns:
                if 'acceso' in str(sub_pattern.pattern):
                    print(f"  {sub_pattern.pattern}")
        if 'acceso' in str(pattern.pattern):
            print(f"{pattern.pattern}")
    except:
        pass
