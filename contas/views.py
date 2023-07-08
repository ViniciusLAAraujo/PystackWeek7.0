from django.shortcuts import render, redirect
from perfil.models import Categoria
from .models import ContaPagar, ContaPaga
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse

# Create your views here.
def definir_contas(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_contas.html', {'categorias': categorias})
    if request.method == "POST":
        titulo = request.POST.get('titulo')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        data_pagamento = request.POST.get('data_pagamento')

        conta = ContaPagar(
            titulo=titulo,
            categoria_id=categoria,
            descricao=descricao,
            valor=valor,
            data_pagamento=data_pagamento
        )

        try:
            conta.save()
        except:
            messages.add_message(request, constants.ERROR, 'Erro ao salvar conta')
            return redirect('/contas/definir_contas')

        messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
        return redirect('/contas/definir_contas')

def ver_contas(request):
    if request.method == "GET":
        #TODONE 01 Add month selection
        TODAY = datetime.now()
        NEARDATE = TODAY + timedelta(days=5)
        overdue_month = request.GET.get('overdue_month')
        try: 
            overdue_month=int(overdue_month)
            if overdue_month < 1 or overdue_month > 12:
                overdue_month = TODAY.month

        except:
            overdue_month = TODAY.month

        contas = ContaPagar.objects.all()

        contas_pagas = ContaPaga.objects.all().values('conta')

        contas_vencidas = contas.filter(data_pagamento__lt=TODAY).exclude(id__in=contas_pagas)

        if overdue_month !=  TODAY.month:
            contas_vencidas_month = contas_vencidas.filter(data_pagamento__month__lte=overdue_month)
        else:
            contas_vencidas_month = contas_vencidas

        contas_proximas_vencimento = contas.filter(data_pagamento__lte = NEARDATE).filter(data_pagamento__gte=TODAY).exclude(id__in=contas_pagas)
        
        restantes = contas.exclude(id__in=contas_vencidas).exclude(id__in=contas_pagas).exclude(id__in=contas_proximas_vencimento)

        return render(request, 'ver_contas.html', {'contas_vencidas': contas_vencidas_month,
                                                    'contas_proximas_vencimento': contas_proximas_vencimento,
                                                    'restantes': restantes,
                                                    'contas_pagas':contas_pagas,
                                                    'current_month':overdue_month})

#TODONE 03  make pagar_conta view to linking it to the buttons "Pagar" in ver_contas.html
@csrf_exempt
def pagar_conta (request,id):
    if request.method == "GET":        
        try: 
            conta_pagar = ContaPagar.objects.get(id=id)

            already_paid = ContaPaga.objects.filter(conta_id=id)
            if already_paid:
                messages.add_message(request, constants.ERROR, f'{conta_pagar.titulo} already paid')
                return redirect('/contas/definir_contas')

            conta_paga = ContaPaga (
                conta_id = conta_pagar.id,
                data_pagamento = datetime.now()
            )
            conta_paga.save()
            messages.add_message(request, constants.SUCCESS, f'{conta_pagar.titulo} successfully paid')
        except:
            messages.add_message(request, constants.ERROR, 'Not a valid Conta Pagar')
            return redirect('/contas/definir_contas')
        
        
        return JsonResponse({'status': 'Success'}) 