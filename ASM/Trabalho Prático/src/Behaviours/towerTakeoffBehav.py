from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle
import math

# Distancia entre dois pontos
def distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Descobre qual a pista disponivel mais proxima da gare
def closest_runway(runways, gare):
    best_runway = None
    min_dist = 1000
    for key, value in runways.items():
        if value["status"] == "free":
            dist = distance(value["location"], gare)
            if dist < min_dist:
                best_runway = key
                min_dist = dist
    return best_runway

# Verifica se existe alguma pista disponível 
def available_runway(runways):
    for key, value in runways.items():
        if value["status"] == "free":
            return True
    return False

class TowerTakeoffBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    async def run(self):

        # Se existirem pistas disponiveis
        if available_runway(self.agent.runways):

            json_data = jsonpickle.encode(self.data)

            # Envia mensagem ao gestor de gares para obter informacoes da gare atual do aviao
            gare_location_request = Message(to="gare@" + XMPP_SERVER)
            gare_location_request.set_metadata("performative", "request_location")
            gare_location_request.body = json_data
            await self.send(gare_location_request)


            # Recebe a resposta do gestor de gares com a localizacao da gare
            gare_response = await self.receive(timeout=1000)
            toDo = gare_response.get_metadata("performative")
            # print(f"Control tower received from gare manager: {toDo}")

            if toDo == "inform_location":
                json_data = gare_response.body
                gare_loc = jsonpickle.decode(json_data)
                plane_jid = str(self.data["id"])
                # print(f"Control tower has the location where {plane_jid} is located.")

                # Calcula a pista mais proxima da gare do aviao
                runway = closest_runway(self.agent.runways, gare_loc)

                if runway:

                    # Altera o estado da pista
                    self.agent.runways[runway]["status"] = "occupied"
                    # print(f"Runway {runway} occupied ...")
                    
                    # Envia a mensagem de confirmacao de descolagem ao aviao
                    data = {"runway": runway}
                    json_data = jsonpickle.encode(data)
                    response_plane = Message(to=plane_jid)
                    response_plane.set_metadata("performative", "agree_takeoff")
                    response_plane.body = json_data
                    await self.send(response_plane)

                    # Adiciona à lista de aviões que estão a levantar
                    self.data["runway"] = runway
                    self.agent.planesTakeoff.append(self.data)

        else:
            # Adiciona a lista de espera de descolagens
            self.agent.takeoffQueue.append(self.data)

            # Envia a mensagem de negacao
            response = Message(to=str(self.data["id"]))
            response.set_metadata("performative", "failure_takeoff")
            response.body = "Takeoff not authorized. No runway available. Added to the takeoff queue."
            await self.send(response)