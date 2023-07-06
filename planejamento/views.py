from django.shortcuts import render
from perfil.models import Categoria
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
        categoria = Categoria.objects.get(id=id)
        categoria.valor_planejamento = novo_valor

        #TODO validate this request

        categoria.save()

        return JsonResponse({'status': 'Success'})
    
def ver_planejamento(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        #TODO 06 fix if values 0 
        return render(request, 'ver_planejamento.html', {'categorias': categorias})