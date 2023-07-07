from django.shortcuts import render,redirect
from perfil.models import Categoria
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib import messages
from django.contrib.messages import constants
from perfil.utils import calcula_total

def definir_planejamento(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        return render(request, 'definir_planejamento.html', {'categorias': categorias})

@csrf_exempt
def update_valor_categoria(request, id):
    if request.method == "POST":
        novo_valor = json.load(request)['novo_valor']
        if ',' in novo_valor:
            novo_valor = novo_valor.replace(',', 'temp').replace('.', ',').replace('temp', '.')

        #TODONE validate this request

        try: 
            float (novo_valor)
        except:
            messages.add_message(request, constants.ERROR, 'Not a valid value')

        try:
            categoria = Categoria.objects.get(id=id)
            categoria.valor_planejamento = novo_valor
            categoria.save()
        except:
            messages.add_message(request, constants.ERROR, "Not a valid id")
            return redirect('/planejamento/definir_planejamento')

        return JsonResponse({'status': 'Success'})
    
def ver_planejamento(request):
    if request.method == "GET":
        try:
            periodo_get =  request.GET.get('periodo')
        except:
            periodo_get = "CM"
        categorias = Categoria.objects.all()
        #TODONE fix if values 0 
        categorias = categorias.filter(valor_planejamento__gt = 0)
        total_categorias_limit =  calcula_total(categorias,'valor_planejamento')
        total_valores_CM = 0
        for c in categorias:
            total_valores_CM += c.total_gasto_CM()

        total_percentages_CM= int((total_valores_CM * 100) / total_categorias_limit)
        

        return render(request, 'ver_planejamento.html', {'categorias': categorias,'periodo_get':periodo_get,'total_categorias_limit':total_categorias_limit,'total_valores_CM':total_valores_CM,'total_percentages_CM':total_percentages_CM})