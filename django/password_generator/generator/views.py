from django.shortcuts import render
import random
# Create your views here.


def home(request):
    return render(request, 'generator/home.html')


def password(request):
    thepassword = ''
    characters = list('abcdefghijklmnopqrstuvwxyz')
    length = int(request.GET.get('length'))
    for x in range(length):
        thepassword += random.choice(characters)
    return render(request, 'generator/password.html', {'password': thepassword})
