from django.urls import path
from . import views

app_name = 'sistema'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
