from django.shortcuts import render

# Create your views here.
def graph(request):

    return render(request, 'graph_app/graph.html')

