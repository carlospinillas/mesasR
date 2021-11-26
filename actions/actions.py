# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


#This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType

#from zoneinfo import ZoneInfo
from datetime import datetime
import locale
from . import fechas_proc
from rasa_sdk.types import DomainDict

###EJEMPLO
class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World!")

        return []


#### Mensaje personalizado de solicitud de acuerdo con disponibilidad


class AskRefCancha(Action):
    def name(self) -> Text:
        return "action_ask_reserva_form_ref_cancha"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        canchas_disp = ['F5','F6','F7','F9']
        horafecha = tracker.get_slot("time_aware")
        print(f"hora tentativa de reserva {horafecha}")
        print(f"canchas disponibles {canchas_disp}")
        dispatcher.utter_message(text=f"Tenemos las siguientes canchas disponibles a esa hora:")
        #imprimir con formato
        lista_texto = ", ".join(canchas_disp)+"."
        dispatcher.utter_message(text=f"{lista_texto}")
        dispatcher.utter_message(text=f"¿Cuál cancha quieres reservar?")

        return []


#####VALIDADORES####

class ValidateReservaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_reserva_form"

    def validate_nombre_reserva(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate name"""

        # If the name is super short, it might be wrong.
        print(f"First name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 2:
            dispatcher.utter_message(text=f"Parece un nombre muy corto, supongo que no es intencional")
            return {"nombre_reserva": None}
        else:
            return {"nombre_reserva": slot_value}
    
    #convertir time a time_aware objeto datetime y validar
    def validate_time_aware(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:

        grain = tracker.latest_message['entities'][0]['additional_info']['values'][0]['grain']
        print(f"grain = {grain}")
        print(type(grain))
        print(len(grain))

        print(f"time duckling = {slot_value}")
        time_aware = fechas_proc.capturar_fecha(slot_value)
        print(f"time aware = {time_aware}")
        hora = time_aware.hour
        print(f"time aware hora = {hora}")
        weekday = time_aware.weekday()
        print(f"time aware weekday = {weekday}")
        #validación inicial, horarios de reserva L-S 8am-9pm D 8am-7pm, se podría implementar
        #calendario de feriados colombianos más adelante

        if grain != 'hour' and grain != 'minute':
            dispatcher.utter_message(text=f"Necesito más detalles, ¿podrías darme la hora también?")
            return {'time' : None, 'time_aware' : None}


        inicio = 8
        final = 21
        if weekday == 6:
          final = 19
        #validar intervalo de horas admisibles
        hora_inicio = time_aware.replace(hour = inicio, minute= 0)
        print(f" hora inicio = {hora_inicio}")
        hora_fin = time_aware.replace(hour = final, minute = 0)
        print(f" hora fin = {hora_fin}")
        dia_texto = fechas_proc.spa_weekday_format(time_aware)
        hora_inicio_texto = fechas_proc.spa_hour12h_format(hora_inicio)
        hora_fin_texto = fechas_proc.spa_hour12h_format(hora_fin)

        #cleanup
        #horas antes de 7 se suponen pm
        if time_aware.hour <= 7:
            newhour = time_aware.hour
            time_aware = time_aware.replace(hour = newhour + 12)
            hora_texto = fechas_proc.spa_hour12h_format(time_aware)
            dispatcher.utter_message(text=f"Supongo que quisiste decir a {hora_texto}")
        
        if not(hora_inicio <= time_aware <= hora_fin):
            dispatcher.utter_message(text=f"No puedo reservar a esa hora, nuestro horario para reservar el {dia_texto} es de {hora_inicio_texto} a {hora_fin_texto}")
            return {"time_aware": None, "time": None}

        #mensaje de horas en punto y más cleanup
        if not time_aware.minute == 0:
            if time_aware.minute <= 30:
                time_aware = time_aware.replace(minute= 0)
            else:
                time_aware = time_aware.replace(hour = time_aware.hour + 1, minute = 0)

            hora_texto = fechas_proc.spa_hour12h_format(time_aware)
            dispatcher.utter_message(text=f"¡Solo puedo reservar a horas en punto! No te preocupes, de forma automática reservaré para {hora_texto}")
      
        
        
        fechatexto = fechas_proc.spa_date_format(time_aware)
        print(f"paso por aca")

        return {"time_reserva": time_aware,"fechatexto": fechatexto}

    def validate_ref_cancha(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        canchas_disp = ['F5','F6','F7','F9']
        #cleanup, upper case
        slot_value = slot_value.upper()
        if slot_value not in canchas_disp:
            dispatcher.utter_message(text=f"No logré entender, por favor escoge una de las opciones")
            return {"ref_cancha" : None}
        
        return {"ref_cancha": slot_value}