from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Prato, Combo, Mesa, Comanda, Item
from .forms import PratoForm, ComboForm, MesaForm, ItemForm, filtrar_periodo
import csv
from django.http import HttpResponse
from .dashboard import obter_metricas_dashboard

# Função auxiliar sugerida na Aula 14 para centralizar a org do usuário logado
def org_atual(request):
    perfil = getattr(request.user, 'perfil', None)
    if perfil is not None:
        return perfil.organizacao

    from core.models import Organizacao, Perfil

    organizacao = Organizacao.objects.order_by('id').first()
    if organizacao is None:
        organizacao = Organizacao.objects.create(nome='Organizacao Principal')
    Perfil.objects.create(usuario=request.user, organizacao=organizacao)
    return organizacao

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
def criar_combo(request):
    org = org_atual(request)
    form = ComboForm(request.POST or None)
    if form.is_valid():
        combo = form.save(commit=False)
        combo.organizacao = org
        combo.save()
        form.save_m2m()
        return redirect('inicio')
    return render(request, 'form.html', {'form': form, 'titulo': 'Novo Combo'})

@login_required
def criar_mesa(request):
    org = org_atual(request)
    form = MesaForm(request.POST or None)
    if form.is_valid():
        mesa = form.save(commit=False)
        mesa.organizacao = org
        mesa.save()
        return redirect('inicio')
    return render(request, 'form.html', {'form': form, 'titulo': 'Nova Mesa'})

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

def _comandas_base_filtradas(request):
    org = org_atual(request)
    qs = Comanda.objects.select_related('mesa').filter(organizacao=org)
    qs_filtrado, form_periodo = filtrar_periodo(request, qs, campo_data='data_hora')
    return org, qs_filtrado, form_periodo

@login_required
def dashboard(request):
    org, comandas_qs, form_periodo = _comandas_base_filtradas(request)
    metricas = obter_metricas_dashboard(org, comandas_qs)
    return render(request, 'dashboard.html', {
        'organizacao': org,
        'form_periodo': form_periodo,
        'kpis': metricas['kpis'],
        'ranking_pratos': metricas['ranking_pratos'],
        'por_mes': metricas['por_mes'],
        'distribuicao_categorias': metricas['distribuicao_categorias'],
    })

@login_required
def exportar_dashboard_csv(request):
    org, comandas_qs, _ = _comandas_base_filtradas(request)
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = 'attachment; filename="relatorio_comandas.csv"'
    writer = csv.writer(resposta)
    writer.writerow(['ID Comanda', 'Mesa', 'Status', 'Total (R$)', 'Data/Hora'])
    for comanda in comandas_qs.order_by('-data_hora'):
        writer.writerow([
            comanda.id,
            comanda.mesa.numero if comanda.mesa else '',
            'Aberta' if comanda.aberta else 'Fechada',
            f'{comanda.total:.2f}',
            comanda.data_hora.strftime('%d/%m/%Y %H:%M') if comanda.data_hora else '',
        ])
    return resposta