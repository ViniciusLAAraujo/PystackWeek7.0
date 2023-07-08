from django.shortcuts import render, redirect
from perfil.utils import calcula_total, calcula_equilibrio_financeiro
from perfil.models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
import imghdr
from django.core.exceptions import ValidationError
from extrato.models import Valores
from contas.models import ContaPaga, ContaPagar
from datetime import datetime, timedelta
#from django.http import HttpResponse
#from django.db.models import Sum

def home(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        saldo_total = calcula_total(contas, 'valor')

        valores = Valores.objects.filter(data__month=datetime.now().month)
        entradas = valores.filter(tipo='E')
        saidas = valores.filter(tipo='S')

        total_entradas = calcula_total(entradas, 'valor')
        total_saidas = calcula_total(saidas, 'valor')

        #TODONE 04 Make home view dynamic for 2 Cards in the right (Saldo total, Gerenciar contas)

        categorias = Categoria.objects.all()
        categorias = categorias.filter(valor_planejamento__gt = 0)
        total_categorias_limit =  calcula_total(categorias,'valor_planejamento')
        total_valores_CM = 0
        for c in categorias:
            total_valores_CM += c.total_gasto_CM()
        total_disp = total_categorias_limit - total_valores_CM

        percentual_gastos_essenciais, percentual_gastos_nao_essenciais = calcula_equilibrio_financeiro()

        TODAY = datetime.now()
        NEARDATE = TODAY + timedelta(days=5)
        contas_pagar = ContaPagar.objects.all()
        contas_pagas = ContaPaga.objects.all().values('conta')
        contas_vencidas = contas_pagar.filter(data_pagamento__lt=TODAY).exclude(id__in=contas_pagas).count()
        contas_proximas_vencimento = contas_pagar.filter(data_pagamento__lte = NEARDATE).filter(data_pagamento__gte=TODAY).exclude(id__in=contas_pagas).count()

        return render(request, 'home.html', {'contas': contas,
                                            'saldo_total': saldo_total,
                                            "total_entradas":total_entradas,
                                            "total_saidas":total_saidas,
                                            "percentual_gastos_essenciais":percentual_gastos_essenciais,
                                            "percentual_gastos_nao_essenciais":percentual_gastos_nao_essenciais,
                                            "total_categorias_limit":total_categorias_limit,
                                            "total_valores_CM":total_valores_CM,
                                            "total_disp":total_disp,
                                            "n_contas_proximas":contas_proximas_vencimento,
                                            "n_contas_vencidas":contas_vencidas})

def gerenciar(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all()
        #total_contas = contas.aggregate(Sum('valor'))
        total_contas = calcula_total(contas, 'valor')
        return render(request, 'gerenciar.html', {'contas': contas, 'total_contas' : total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    if request.method == "POST":
        apelido = request.POST.get('apelido')
        banco = request.POST.get('banco')
        tipo = request.POST.get('tipo')
        valor = request.POST.get('valor')
        icone = request.FILES.get('icone')

        baseAcc = Conta.objects.first()
        valid_banco_choices = dict(baseAcc.banco_choices).keys()
        valid_tipo_choices = dict(baseAcc.tipo_choices).keys()

        if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Fill all from camps')
            return redirect('/perfil/gerenciar/')
        
        if not icone:
            messages.add_message(request, constants.ERROR, 'Icon is required')
            return redirect('/perfil/gerenciar/')
        
        image_type = imghdr.what(icone)
        
        if image_type not in ['png', 'jpeg','jpg']:
            messages.add_message(request, constants.ERROR, 'Icon must be a valid image')
            return redirect('/perfil/gerenciar/')
        
        if banco not in valid_banco_choices:
            messages.add_message(request, constants.ERROR, 'Not a valid bank')
            return redirect('/perfil/gerenciar/')
            pass

        if tipo not in valid_tipo_choices:
            messages.add_message(request, constants.ERROR, 'Not a valid type')
            return redirect('/perfil/gerenciar/')
            pass

        #TODONE validate other fields
        
        conta = Conta(
            apelido = apelido,
            banco=banco,
            tipo=tipo,
            valor=valor,
            icone=icone
        )

        try:
            conta.save()
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')
        
        messages.add_message(request, constants.SUCCESS, 'Account was created!')
        return redirect('/perfil/gerenciar/')


def deletar_banco(request, id):
    if request.method == "GET":
        try:
            conta = Conta.objects.get(id=id)
            try:
                conta.delete()
            except:
                messages.add_message(request, constants.ERROR, 'Erro ao deletar, verifique se não existem registros relacionados')
                return redirect('/perfil/gerenciar/')
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')
        
        
        messages.add_message(request, constants.SUCCESS, 'Account deleted!')
        return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    if request.method == "POST":
        nome = request.POST.get('categoria')
        essencial = bool(request.POST.get('essencial'))


        if len(nome.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Categories need names')
            return redirect('/perfil/gerenciar/')
        
        #TODONE validate category form camps

        categoria = Categoria(
            categoria=nome,
            essencial=essencial
        )

        try:
            categoria.save()
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')

        messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
        return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    if request.method == "GET":
        
        try:
            categoria = Categoria.objects.get(id=id)

            categoria.essencial = not categoria.essencial

            categoria.save()
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')
        
        print("will return try")
        return redirect('/perfil/gerenciar/')

def deletar_categoria(request, id):
    if request.method == "GET":
        try:
            conta = Categoria.objects.get(id=id)
            try:
                conta.delete()
            except:
                messages.add_message(request, constants.ERROR, 'Erro ao deletar, verifique se não existem registros relacionados')
                return redirect('/perfil/gerenciar/')
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')

        
        messages.add_message(request, constants.SUCCESS, 'Category deleted!')
        return redirect('/perfil/gerenciar/')
    
def dashboard(request):
    if request.method == "GET":
        dados = {}
        categorias = Categoria.objects.all()

        for categoria in categorias:
            dados[categoria.categoria] = calcula_total(Valores.objects.filter(categoria=categoria),'valor')

        return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})