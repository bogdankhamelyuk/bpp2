from django.urls import path
from . import views
from graph_app.views import graph,getPressure

urlpatterns = [
    path('', views.home,name="home"),
    path('/graph', graph),
]

