from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/sistema/', permanent=False)),
    path('', include('accounts.urls', namespace='accounts')),
    path('sistema/', include('sistema.urls', namespace='sistema')),
]
