from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth
from .models import Comanda, Item, Prato

def obter_metricas_dashboard(org, comandas_qs):
    kpis = comandas_qs.aggregate(
        total_comandas=Count('id'),
        abertas=Count('id', filter=Q(aberta=True)),
        fechadas=Count('id', filter=Q(aberta=False)),
        faturamento=Sum('total', filter=Q(aberta=False)),
    )
    kpis['faturamento'] = kpis['faturamento'] or 0

    itens_qs = (
        Item.objects
        .select_related('prato', 'comanda')
        .filter(
            comanda__organizacao=org,
            comanda__in=comandas_qs,
            prato__isnull=False,
        )
    )
    ranking_pratos = list(
        itens_qs
        .values('prato__nome')
        .annotate(quantidade_total=Sum('quantidade'))
        .order_by('-quantidade_total')[:5]
    )

    por_mes_qs = (
        comandas_qs
        .annotate(mes=TruncMonth('data_hora'))
        .values('mes')
        .annotate(
            quantidade_comandas=Count('id'),
            receita=Sum('total'),
        )
        .order_by('mes')
    )
    por_mes = [
        {
            'mes': linha['mes'].strftime('%m/%Y') if linha['mes'] else 'Sem data',
            'total': linha['quantidade_comandas'],
            'receita': float(linha['receita'] or 0),
        }
        for linha in por_mes_qs
    ]

    distribuicao_categorias = list(
        Prato.objects
        .filter(organizacao=org)
        .values('categoria')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    return {
        'kpis': kpis,
        'ranking_pratos': ranking_pratos,
        'por_mes': por_mes,
        'distribuicao_categorias': distribuicao_categorias,
    }