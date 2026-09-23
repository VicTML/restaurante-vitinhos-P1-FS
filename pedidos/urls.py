from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('novo-prato/', views.criar_prato, name='criar_prato'),
    path('novo-combo/', views.criar_combo, name='criar_combo'),
    path('nova-mesa/', views.criar_mesa, name='criar_mesa'),
    path('abrir-comanda/<int:mesa_id>/', views.abrir_comanda, name='abrir_comanda'),
    path('comanda/<int:comanda_id>/', views.detalhe_comanda, name='detalhe_comanda'),
    path('fechar-conta/<int:comanda_id>/', views.fechar_conta, name='fechar_conta'),
]