from django.shortcuts import render
from django.views.generic import TemplateView


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure_view_setting(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def custom_500_view(request):
    return render(request, 'pages/500.html', status=500)


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'
