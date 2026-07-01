from django.shortcuts import render

from example.view_data import DEMO_VIEW_DATA, render_view_data


def home(request):
    return render(request, "home.html")


def dynamic_home(request):
    page_html = render_view_data(DEMO_VIEW_DATA, request=request)
    return render(request, "dynamic.html", {"page_html": page_html})
