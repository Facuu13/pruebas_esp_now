import json
import re

# /sensor/08b61f811920/enable/set
class MessageProcessor:
    @staticmethod
    def extraer_mac(topic):
        """
        Extrae el mac del topic que sigue a /sensor/
        """
        match = re.search(r'/sensor/([^/]+)(?:/|$)', topic)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def extraer_accion(topic):
        """
        Extrae la acción del topic que sigue a la MAC.
        """
        match = re.search(r'/sensor/[^/]+/([^/]+/[^/]+)$', topic)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def validar_mac(mac_propia, identifier):
        """
        Valida si el identifier es igual a la mac_propia.
        """
        if identifier == mac_propia:
            print("Son la misma MAC")
            return True
        else:
            print("Diferente MAC")
            return False

    @staticmethod
    def procesar_mensaje(mac_propia, mac, msg, acciones):
        """
        Procesa el mensaje recibido, convirtiéndolo en un formato adecuado.
        """
        try:
            data = json.loads(msg)
            topic = data.get("topic")
            value = data.get("value")
            if topic and value is not None:
                print("Topic_general:", topic)
                print("Value:", value)

                # Extraer la mac 
                identifier = MessageProcessor.extraer_mac(topic)
                if identifier and MessageProcessor.validar_mac(mac_propia, identifier):
                    accion = MessageProcessor.extraer_accion(topic)

                    # Busca la función asociada a la acción en el diccionario
                    if accion in acciones:
                        acciones[accion](value)  # Llama a la función correspondiente
                    else:
                        print(f"Acción desconocida: {accion}")
            else:
                print("No se pudo extraer el identificador del topic")

        except Exception as ex:
            print("Error procesando el mensaje:", ex)

