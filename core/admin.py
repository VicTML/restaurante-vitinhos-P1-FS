from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Organizacao, Perfil

admin.site.register(Organizacao)
admin.site.register(Perfil)