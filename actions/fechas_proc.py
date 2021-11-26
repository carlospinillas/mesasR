#from zoneinfo import ZoneInfo
from datetime import datetime
import locale
#import pytz

#acepta objeto datetime tz aware y genera string de texto
def spa_date_format(date):
    locale.setlocale(locale.LC_ALL, 'es_CO')

    #singular para la 1am y la 1pm
    if (date.hour == 1 or date.hour == 13):
       plural=" "
    else:
       plural="s "
    #formato: weekday day_number month year hour:minute ampm
    messsage = date.strftime("%A %d de %B de %Y a la"+plural+"%I:%M %p")

    return messsage

def spa_weekday_format(date):
    locale.setlocale(locale.LC_ALL, 'es_CO')
    messsage = date.strftime("%A")

    return messsage

def spa_hour12h_format(date):
    if (date.hour == 1 or date.hour == 13):
        plural=" "
    else:
        plural="s "
    locale.setlocale(locale.LC_ALL, 'es_CO')
    messsage = date.strftime("la"+plural+"%I:%M%p")

    return messsage


#captura fecha en objeto date time aware
def capturar_fecha(fechahora_col):
    # ejemplo 2021-11-07T15:00:00.000-05:00
    #local_time = pytz.timezone("America/Bogota")
    #convertir a 2021-11-07T15:00:00.000-0500, eliminando el : en el utc offset
    fechahora_col = fechahora_col[0:-3]+fechahora_col[-2:]
    #date_time_str = '2018-06-29 08:15:27.243860'
    aware_datetime = datetime.strptime(fechahora_col, '%Y-%m-%dT%H:%M:%S.%f%z')
    
    return aware_datetime

now = datetime.now()
datestr = '2021-11-07T13:00:00.000-05:00'
date = capturar_fecha(datestr)
print(now.hour)
print(spa_date_format(now))
print(now)
print(date)
print(spa_date_format(date))