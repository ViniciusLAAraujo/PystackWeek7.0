from django.shortcuts import render, redirect
from perfil.models import Conta, Categoria
from .models import Valores
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime
from django.template.loader import render_to_string
import os
from django.conf import settings
from weasyprint import HTML
from io import BytesIO
from django.http import FileResponse
from .utils import filterValues


# Create your views here.

def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all() 
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')

        if ',' in valor:
            valor = valor.replace(',', 'temp').replace('.', ',').replace('temp', '.')
        
        # try: 
        #     datetime (data)
        # except:
        #     messages.add_message(request, constants.ERROR, 'Not a valid date')
        #     return redirect('/extrato/novo_valor')

        try: 
            float (valor)
        except:
            messages.add_message(request, constants.ERROR, 'Not a valid value')

        if len(valor.strip()) == 0 or len(descricao.strip()) == 0  or len(data.strip()) == 0:
            messages.add_message(request, constants.ERROR, 'Entries must have value, description, and date')
            return redirect('/extrato/novo_valor')
        
        try:
            Conta.objects.get(id=conta)
        except:
            messages.add_message(request, constants.ERROR, 'Not a valid account')
            return redirect('/extrato/novo_valor')
            
        try:
            Categoria.objects.get(id=categoria)
        except:
            messages.add_message(request, constants.ERROR, 'Not a valid category')
            return redirect('/extrato/novo_valor')
            
        baseType = Valores.objects.first()
        valid_types = dict(baseType.choice_tipo).keys()
        if  tipo not in valid_types:
            messages.add_message(request, constants.ERROR, 'Not a valid Type')
            return redirect('/extrato/novo_valor')

        

        #TODONE validate this form

        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)

        if tipo == 'E':
            conta.valor += float(valor)
            messages.add_message(request, constants.SUCCESS, 'Entrada ')
        else:
            conta.valor -= float(valor)
            messages.add_message(request, constants.SUCCESS, 'Saida ')

        conta.save()

        
        #TODONE message should be acordding to type
        messages.add_message(request, constants.SUCCESS, 'cadastrada com sucesso')
        return redirect('/extrato/novo_valor')
    
def view_extrato(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all()

            
        

        conta_get = request.GET.get('conta')
        categoria_get = request.GET.get('categoria')
        periodo_get =  request.GET.get('periodo')

        if periodo_get in filterValues:
            valores = filterValues[periodo_get]()
        else:
            valores = Valores.objects.filter(data__month=datetime.now().month)

        #TODONE validate form and add dynamic time range. Also add neutral to filters
        #TODONE clear filters button 

        if conta_get and  conta_get != "--":
            valores = valores.filter(conta__id=conta_get)
        if categoria_get and categoria_get != "--":
            valores = valores.filter(categoria__id=categoria_get)
    

        return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias})
    
def exportar_pdf(request):
    if request.method == "GET":
        valores = Valores.objects.filter(data__month=datetime.now().month)
        contas = Conta.objects.all()
        categorias = Categoria.objects.all()
        
        path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
        path_output = BytesIO()

        template_render = render_to_string(path_template, {'valores': valores, 'contas': contas, 'categorias': categorias})
        HTML(string=template_render).write_pdf(path_output)

        path_output.seek(0)
        

        return FileResponse(path_output, filename="extrato.pdf")