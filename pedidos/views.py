from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q 
from .models import Prato, Combo, Mesa, Comanda, Item
from .forms import PratoForm, ComboForm, MesaForm, ItemForm

def inicio(request):
    mesas = Mesa.objects.all()
    comandas_abertas = Comanda.objects.filter(aberta=True)
    
    pratos = Prato.objects.all()
    
    query = request.GET.get('q')
    categoria = request.GET.get('categoria')

    if query or categoria:
        filtros = Q()
        if query:
            filtros &= Q(nome__icontains=query)
        if categoria:
            filtros &= Q(categoria=categoria)
            
        pratos = pratos.filter(filtros)

    return render(request, 'inicio.html', {
        'mesas': mesas, 
        'comandas_abertas': comandas_abertas,
        'pratos': pratos, 
    })

# --- VIEWS EXTRAS (Criar Prato, Combo e Mesa) ---
def criar_prato(request):
    form = PratoForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('inicio')
    return render(request, 'form.html', {'form': form, 'titulo': 'Novo Prato'})

def criar_combo(request):
    form = ComboForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('inicio')
    return render(request, 'form.html', {'form': form, 'titulo': 'Novo Combo'})

def criar_mesa(request):
    form = MesaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('inicio')
    return render(request, 'form.html', {'form': form, 'titulo': 'Nova Mesa'})

# --- LÓGICA DA P1 (Comanda e Fechamento) ---
def abrir_comanda(request, mesa_id):
    mesa = get_object_or_404(Mesa, id=mesa_id)
    if not mesa.ocupada:
        # Cria a comanda e marca a mesa como ocupada
        Comanda.objects.create(mesa=mesa)
        mesa.ocupada = True
        mesa.save()
    return redirect('inicio')

def detalhe_comanda(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    itens = Item.objects.filter(comanda=comanda)
    
    # Calcula o total parcial
    total_parcial = sum(
        (item.prato.preco * item.quantidade if item.prato else 0) +
        (item.combo.preco * item.quantidade if item.combo else 0)
        for item in itens
    )
    
    form = ItemForm(request.POST or None)
    if form.is_valid():
        novo_item = form.save(commit=False)
        novo_item.comanda = comanda
        novo_item.save()
        return redirect('detalhe_comanda', comanda_id=comanda.id)
        
    return render(request, 'comanda_detalhe.html', {
        'comanda': comanda, 'itens': itens, 'form': form, 'total_parcial': total_parcial
    })

def fechar_conta(request, comanda_id):
    comanda = get_object_or_404(Comanda, id=comanda_id)
    itens = Item.objects.filter(comanda=comanda)
    
    # Calcula total final
    total = sum(
        (item.prato.preco * item.quantidade if item.prato else 0) +
        (item.combo.preco * item.quantidade if item.combo else 0)
        for item in itens
    )
    
    # Atualiza a comanda
    comanda.total = total
    comanda.aberta = False
    comanda.save()
    
    # Libera a mesa
    mesa = comanda.mesa
    mesa.ocupada = False
    mesa.save()
    
    return redirect('inicio')