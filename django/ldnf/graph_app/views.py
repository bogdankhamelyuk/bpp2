from django.shortcuts import render
from .models import Message
# Create your views here.
def graph(request):
    measures = Message.objects.all()
    #print(measures.latest('id'))
    print(measures.values_list('id')[0])
    context = {
        'measures' : measures,
    }
    return render(request, 'graph_app/graph.html', context)

