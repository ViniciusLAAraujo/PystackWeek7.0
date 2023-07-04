from django.shortcuts import render, redirect
from .utils import calcula_total
from .models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
#from django.http import HttpResponse
#from django.db.models import Sum

def home(request):
    contas = Conta.objects.all()
    saldo_total = calcula_total(contas, 'valor')
    return render(request, 'home.html', {'contas': contas, 'saldo_total': saldo_total,})

def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    #total_contas = contas.aggregate(Sum('valor'))
    total_contas = calcula_total(contas, 'valor')
    return render(request, 'gerenciar.html', {'contas': contas, 'total_contas' : total_contas, 'categorias': categorias})

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Fill all from camps')
        return redirect('/perfil/gerenciar/')
    
    #TODO validate other fields
    
    conta = Conta(
        apelido = apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()
    messages.add_message(request, constants.SUCCESS, 'Account was created!')
    return redirect('/perfil/gerenciar/')


def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()
    
    messages.add_message(request, constants.SUCCESS, 'Account deleted!')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    #TODO validate category form camps

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    return redirect('/perfil/gerenciar/')

def deletar_categoria(request, id):
    conta = Categoria.objects.get(id=id)
    conta.delete()
    
    messages.add_message(request, constants.SUCCESS, 'Category deleted!')
    return redirect('/perfil/gerenciar/')