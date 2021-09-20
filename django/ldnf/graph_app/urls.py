
from django.urls import path
from . import views
from . import consumers
from home_app.views import home

urlpatterns = [
    path('', views.graph),
    path('/',home),
    
    
]