from datetime import datetime,timedelta
from extrato.models import Valores

def filter_values_current_month():
    return Valores.objects.filter(data__month=datetime.now().month)

def filter_values_last_7days():
    start_date = datetime.now() - timedelta(days=7)
    return Valores.objects.filter(data__gte=start_date)

def filter_values_previous_month():
    first_day_of_current_month = datetime.now().replace(day=1)
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    previous_month = last_day_of_previous_month.month
    return Valores.objects.filter(data__month=previous_month)


filterValues = {
    "CM":filter_values_current_month,
    "L7":filter_values_last_7days,
    "PM":filter_values_previous_month
    }
