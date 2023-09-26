from django.shortcuts import render


def show_index_page(request):
    return render(request, 'index.html')
