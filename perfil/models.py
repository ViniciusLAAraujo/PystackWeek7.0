from django.db import models
from datetime import datetime, timedelta
from .utils import calcula_total
# Create your models here.

class Categoria(models.Model):
    categoria = models.CharField(max_length=50)
    essencial = models.BooleanField(default=False)
    valor_planejamento = models.FloatField(default=0)

    def __str__(self):
        return self.categoria
    
    #TODONE make it so total_gasto could recive time ranges
    def valor_planejamento_div7(self):
        return format(self.valor_planejamento/7,'.2f')

    def total_gasto_CM(self):
        from extrato.models import Valores

        valores = Valores.objects.filter(categoria__id = self.id).filter(data__month=datetime.now().month).filter(tipo='S')
        #TODONE use calcula total from utils
        valores = calcula_total(valores,'valor')
        return valores if valores else 0
    
    def total_gasto_L7(self):
        from extrato.models import Valores
        start_date = datetime.now() - timedelta(days=7)
        valores = Valores.objects.filter(categoria__id = self.id).filter(data__gte=start_date).filter(tipo='S')
        #TODONE use calcula total from utils
        valores = calcula_total(valores,'valor')
        return valores if valores else 0
    
    def total_gasto_PM(self):
        from extrato.models import Valores
        first_day_of_current_month = datetime.now().replace(day=1)
        last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
        previous_month = last_day_of_previous_month.month
        valores = Valores.objects.filter(categoria__id = self.id).filter(data__month=previous_month).filter(tipo='S')
        #TODONE use calcula total from utils
        valores = calcula_total(valores,'valor')
        return valores if valores else 0

    def calcula_percentual_gasto_por_categoria_CM(self):
        #try to catch ZeroDivisionError 
        try:
            return int((self.total_gasto_CM() * 100) / self.valor_planejamento)
        except:
            return 0
    def calcula_percentual_gasto_por_categoria_L7(self):
        #try to catch ZeroDivisionError 
        try:
            return int((self.total_gasto_L7() * 100) / self.valor_planejamento)
        except:
            return 0
    def calcula_percentual_gasto_por_categoria_PM(self):
        #try to catch ZeroDivisionError 
        try:
            return int((self.total_gasto_PM() * 100) / self.valor_planejamento)
        except:
            return 0

class Conta(models.Model):
    banco_choices = (
        ('NU', 'Nubank'),
        ('IT', 'Itau'),
        ('BR', 'Bradesco'),
        ('ST', 'Santander'),
        ('CE', 'Caixa econômica'),
    )

    tipo_choices = (
        ('PF', 'Pessoa física'),
        ('PJ', 'Pessoa jurídica'),
    )

    apelido = models.CharField(max_length=50)
    banco = models.CharField(max_length=2, choices=banco_choices)
    tipo = models.CharField(max_length=2, choices=tipo_choices)
    valor = models.FloatField()
    icone = models.ImageField(upload_to='icones')

    def __str__(self):
        return self.apelido