from django.shortcuts import render, redirect
from .utils import calcula_total
from .models import Conta, Categoria
from django.contrib import messages
from django.contrib.messages import constants
import imghdr
from django.core.exceptions import ValidationError
#from django.http import HttpResponse
#from django.db.models import Sum

def home(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        saldo_total = calcula_total(contas, 'valor')
        return render(request, 'home.html', {'contas': contas, 'saldo_total': saldo_total,})

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
    if request.method == "POST":
        try:
            conta = Conta.objects.get(id=id)
            conta.delete()
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
    if request.method == "POST":
        
        try:
            categoria = Categoria.objects.get(id=id)

            categoria.essencial = not categoria.essencial

            categoria.save()
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')

        return redirect('/perfil/gerenciar/')

def deletar_categoria(request, id):
    if request.method == "POST":
        try:
            conta = Categoria.objects.get(id=id)
            conta.delete()
        except ValidationError as e:
            error_message = e.message_dict['name'][0]
            messages.add_message(request, constants.ERROR, f'{error_message}')
            return redirect('/perfil/gerenciar/')

        
        messages.add_message(request, constants.SUCCESS, 'Category deleted!')
        return redirect('/perfil/gerenciar/')