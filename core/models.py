from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Organizacao(models.Model):
    nome = models.CharField(max_length=120)
    criada_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class DaOrganizacao(models.Model):
    organizacao = models.ForeignKey(
        Organizacao, 
        on_delete=models.PROTECT
    )

    class Meta:
        abstract = True  # O Django não cria tabela para esta classe, apenas copia os campos

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    organizacao = models.ForeignKey(Organizacao, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.usuario.username} - {self.organizacao.nome}"