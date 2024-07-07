from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect


def home_view(request):
    return render(request, 'index.html')


def custom_404(request, exception=None):
    return JsonResponse({'error': 'Sahifa topilmadi'}, status=404)


def custom_500(request):
    return JsonResponse({'error': 'Server Error'}, status=500)


def custom_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_superuser:
                login(request, user)
                return HttpResponseRedirect('/docs/swagger/')
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


def custom_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')
