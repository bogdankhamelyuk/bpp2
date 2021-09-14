from django.urls import path
from . import views
import graph_app
from graph_app.views import graph
urlpatterns = [
    path('', views.home,name="home"),
    path('/graph', graph),

]

