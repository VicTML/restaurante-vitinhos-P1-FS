from django.db import models

# Create your models here.

class Prato(models.Model):
    CATEGORIAS_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Principal', 'Prato Principal'),
        ('Sobremesa', 'Sobremesa'),
        ('Bebida', 'Bebida'),
    ]
    
    nome = models.CharField(max_length=50)
    ingredientes = models.TextField()
    preco = models.DecimalField(max_digits=5, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_CHOICES, default='Principal')

    def __str__(self):
        return self.nome

class Combo(models.Model):
    nome = models.CharField(max_length=50)
    pratos = models.ManyToManyField(Prato)
    preco = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.nome

class Mesa(models.Model):
    numero = models.IntegerField()
    capacidade = models.IntegerField()
    ocupada = models.BooleanField(default=False)

    def __str__(self):
        return f"Mesa {self.numero}"

class Comanda(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    aberta = models.BooleanField(default=True)
    data_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comanda {self.id} - Mesa {self.mesa.numero}"

class Item(models.Model):
    comanda = models.ForeignKey(Comanda, on_delete=models.CASCADE)
    prato = models.ForeignKey(Prato, on_delete=models.CASCADE, null=True, blank=True)
    combo = models.ForeignKey(Combo, on_delete=models.CASCADE, null=True, blank=True)
    quantidade = models.IntegerField(default=1)

    def __str__(self):
        return f"Item {self.id} da Comanda {self.comanda.id}"