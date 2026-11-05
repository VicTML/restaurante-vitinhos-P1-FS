from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Prato, Combo, Mesa, Comanda, Item
from .forms import PratoForm, ComboForm, MesaForm, ItemForm

# Função auxiliar sugerida na Aula 14 para centralizar a org do usuário logado
def org_atual(request):
    return request.user.perfil.organizacao

@login_required
def inicio(request):
    org = org_atual(request)
    # Filtra rigorosamente apenas os dados da organização do usuário logado
    mesas = Mesa.objects.filter(organizacao=org)
    comandas_abertas = Comanda.objects.filter(organizacao=org, aberta=True)
    
    pratos = Prato.objects.filter(organizacao=org)
    query = request.GET.get('q')
    categoria = request.GET.get('categoria')

    if query or categoria:
        filtros = Q(organizacao=org) # Mantém o isolamento na busca
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

@login_required
def criar_prato(request):
    org = org_atual(request)
    form = PratoForm(request.POST or None)
    if form.is_valid():
        prato = form.save(commit=False)
        prato.organizacao = org  # Associa automaticamente à organização correta
        prato.save()
        return redirect('inicio')
    return render(request, 'form.html', {'form': form, 'titulo': 'Novo Prato'})

@login_required
def abrir_comanda(request, mesa_id):
    org = org_atual(request)
    # BLINDAGEM: Se tentar acessar uma mesa de outra org via URL, gera 404 e protege o sistema!
    mesa = get_object_or_404(Mesa, id=mesa_id, organizacao=org)
    
    if not mesa.ocupada:
        Comanda.objects.create(mesa=mesa, organizacao=org)
        mesa.ocupada = True
        mesa.save()
    return redirect('inicio')

@login_required
def detalhe_comanda(request, comanda_id):
    org = org_atual(request)
    comanda = get_object_or_404(Comanda, id=comanda_id, organizacao=org)
    itens = Item.objects.filter(comanda=comanda)
    
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

@login_required
def fechar_conta(request, comanda_id):
    org = org_atual(request)
    comanda = get_object_or_404(Comanda, id=comanda_id, organizacao=org)
    itens = Item.objects.filter(comanda=comanda)
    
    total = sum(
        (item.prato.preco * item.quantidade if item.prato else 0) +
        (item.combo.preco * item.quantidade if item.combo else 0)
        for item in itens
    )
    
    comanda.total = total
    comanda.aberta = False
    comanda.save()
    
    mesa = comanda.mesa
    mesa.ocupada = False
    mesa.save()
    
    return redirect('inicio')

# (Adicione a mesma lógica de @login_required e filtro por organizacao para criar_combo e criar_mesa)