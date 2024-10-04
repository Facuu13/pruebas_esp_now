import json
import re

# /sensor/f412fa80a7f0/rele/set/1
class MessageProcessor:

    def extraer_mac(topic):
        """
        Extrae el mac del topic que sigue a /sensor/
        """
        match = re.search(r'/sensor/([^/]+)(?:/|$)', topic)
        if match:
            return match.group(1)
        return None


    def extraer_accion(topic):
        """
        Extrae la acción del topic que sigue a la MAC.
        """
        match = re.search(r'/sensor/[^/]+/([^/]+/[^/]+)', topic)
        if match:
            return match.group(1)
        return None


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
    

    def extraer_numero_rele(topic):
        """
        Extrae el número del relé desde el topic.
        """
        match = re.search(r'/rele/set/(\d+)$', topic)
        if match:
            return int(match.group(1))
        return None


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
                    # Extraer la acción
                    accion = MessageProcessor.extraer_accion(topic)
                    if accion in acciones:
                        if accion == "rele/set":
                            rele_numero = MessageProcessor.extraer_numero_rele(topic)
                            print("numero de rele:", rele_numero)
                            if rele_numero:
                                acciones[accion](rele_numero, value)
                            else:
                                print("No se pudo extraer el número de relé")
                        
                        else:
                            # Para otras acciones que no requieren número de relé 
                            # y aca podemos agregar otras acciones
                            acciones[accion](value)  # Llama a la función correspondiente
                    else:
                        print(f"Acción desconocida: {accion}")
            else:
                print("No se pudo extraer el identificador del topic")

        except Exception as ex:
            print("Error procesando el mensaje:", ex)

