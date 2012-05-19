from django.shortcuts import render


def homepage(request):
    context = {}
    return render(request, 'homepage.html', context)


def about(request):
    context = {}
    return render(request, 'about.html', context)


def help_page(request):
    context = {}
    return render(request, 'help.html', context)


def legal(request):
    context = {}
    return render(request, 'legal.html', context)
