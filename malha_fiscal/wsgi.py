"""
WSGI config for malha_fiscal project.
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'malha_fiscal.settings')

application = get_wsgi_application()

# ── Auto-migrate no cold start (Vercel serverless) ───────────────────────────
# O buildCommand do vercel.json nem sempre roda migrations em ambiente legado.
# Aqui garantimos que as migrations são aplicadas a cada cold start.
# Com zero migrations pendentes o custo é < 200ms (só lê django_migrations).
if os.environ.get('DATABASE_URL'):
    try:
        from django.core.management import call_command
        call_command('migrate', '--noinput', verbosity=0)
    except Exception as exc:
        print(f'[wsgi] migrate falhou: {exc}', file=sys.stderr)
