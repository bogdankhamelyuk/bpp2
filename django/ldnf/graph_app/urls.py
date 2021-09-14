
from django.urls import path
from . import views

from home_app.views import home

urlpatterns = [
    path('', views.graph),
    path('/',home),
    
]

