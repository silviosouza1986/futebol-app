from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_jogos, name='lista_jogos'),
    path('buscajogos', views.busca_jogos, name='busca_jogos'),
]