"""
URL configuration for qkd_simulation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from simulator import views as simulatorView
from generate_key import views as gereateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('simulate/', simulatorView.simulate, name='simulate'),
    path('generate-key/', gereateView.generate_key, name='generate_key'),
    path('get-csrf-token/', simulatorView.get_csrf_token, name='get_csrf_token'),
    path('show-qcircuits/', simulatorView.show_qcircuits, name='show_qcircuits'),
    path('encrypt/', simulatorView.encrypt, name='encrypt'),
    path('decrypt/', simulatorView.decrypt, name='decrypt'),
    path('correct/', simulatorView.correct_key, name='correct_key'),
    path('encryptAES/', simulatorView.encryptAES, name='encryptAES'),
    path('decryptAES/', simulatorView.decryptAES, name='decryptAES'),
    
]
