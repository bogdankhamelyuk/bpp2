from django.shortcuts import render
from .models import Pressure#, Time
from django.http import JsonResponse
# Create your views here.
def graph(request):
   
    pressure = Pressure.objects.all()
    #print(measures.latest('number_of_measure'))
    #print(pressure.latest('pressure'))
    #print(time.latest('timestamp'))
  
    return render(request, 'graph_app/graph.html')

def getPressure(request):
    pressure = Pressure.objects.last()
    
    return JsonResponse({"time":pressure.timestamp,"pressure":pressure.pressure})
