from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='index.html'), name='landing'),
    path('', include('accounts.urls', namespace='accounts')),
    path('sistema/', include('sistema.urls', namespace='sistema')),
    path('privacidade/', TemplateView.as_view(template_name='legal/privacidade.html'), name='privacidade'),
    path('termos/',      TemplateView.as_view(template_name='legal/termos.html'),      name='termos'),
]
