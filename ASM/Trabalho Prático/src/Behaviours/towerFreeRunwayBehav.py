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

# Verifica se existe alguma pista disponível 
def available_runway(runways):
    for key, value in runways.items():
        if value["status"] == "free":
            return True
    return False

# Verifica o menor caminho entre as pistas e gares disponiveis
def shortest_path(runways, gares):
    best_runway = None
    best_gare = None
    min_dist = 1000
    for key1, value1 in runways.items():
        if value1["status"] == "free":
            for key2, value2 in gares.items():
                dist = distance(value1["location"], value2["location"])
                if dist < min_dist:
                    best_runway = key1
                    best_gare = key2
                    min_dist = dist
    return (best_runway, best_gare)

# Descobre qual a pista disponivel mais perto da gare
def closest_runway(runways, gare):
    best_runway = None
    min_dist = 1000
    for key, value in runways.items():
        if value["status"] == "free":
            print(f"gare: {gare}")
            dist = distance(value["location"], gare)
            if dist < min_dist:
                best_runway = key
                min_dist = dist
    return best_runway

class TowerFreeRunwayBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    async def run(self):

        # Liberta a pista
        self.agent.runways[self.data]["status"] = "free"
        # print(f"Runway {str(self.data)} is now free")


        # Iterar sobre a lista e remover os aviões
        for plane in self.agent.landingQueue:
            # Verifica se existe alguma gare para o tipo de avião que está a iterar
            available_gares = Message(to="gare@" + XMPP_SERVER)
            available_gares.set_metadata("performative", "request")
            json_data = jsonpickle.encode(plane)
            available_gares.body = json_data
            await self.send(available_gares)

            gare_response = await self.receive(timeout=1000)
            toDo = gare_response.get_metadata("performative")
            # print(f"Control tower received from gare manager: {toDo}")

            if toDo == "inform":
                gare_list = jsonpickle.decode(gare_response.body)

                # Verifica que a lista não veio vazia
                if gare_list:
                    runway, gare = shortest_path(self.agent.runways, gare_list)

                    if runway and gare and plane in self.agent.landingQueue:
                        jid_plane = str(plane["id"])

                        # Remove aviao da lista de espera de aterragem
                        self.agent.landingQueue.remove(plane)
                        # print(f"Control tower removed plane {jid_plane} from the landing queue.")

                        # Atualiza a informação do avião e adiciona à lista de aviões que estão aterrar
                        plane["runway"] = runway
                        plane["gare"] = gare
                        self.agent.planesLanding.append(plane)     

                        # Altera o estado da pista
                        self.agent.runways[runway]["status"] = "occupied"
                        # print(f"Runway {runway} occupied ...")

                        # Envia a mensagem de ocupacao da gare para o gestor de gares
                        gare_occupy = Message(to="gare@" + XMPP_SERVER)
                        gare_occupy.set_metadata("performative", "request_occupy")
                        json_data = jsonpickle.encode(gare)
                        gare_occupy.body = json_data
                        # print(f"Control tower informing which gare the plane is going to use to gare manager...")
                        await self.send(gare_occupy)

                        # Envia a mensagem de confirmacao para o aviao
                        response_plane = Message(to=jid_plane)
                        response_plane.set_metadata("performative", "agree_landing")
                        landing_info = {"runway": runway, "gare": gare}


                        json_data = jsonpickle.encode(landing_info)
                        response_plane.body = json_data
                        await self.send(response_plane)
                        # print(f"Control tower sending landing confirmation to {jid_plane}")

        # Percorre a lista de espera de descolagens
        for plane in self.agent.takeoffQueue:

            # Envia mensagem ao gestor de gares para obter informacoes da gare atual do aviao
            gare_location_request = Message(to="gare@" + XMPP_SERVER)
            gare_location_request.set_metadata("performative", "request_location")
            gare_location_request.body = jsonpickle.encode(plane)
            await self.send(gare_location_request)
                
            gare_response = await self.receive(timeout=1000)
            toDo = gare_response.get_metadata("performative")
            # print(f"Control tower received from gare manager: {toDo}")

            if toDo == "inform_location":

                json_data = gare_response.body
                gare_loc = jsonpickle.decode(json_data)

                runway = closest_runway(self.agent.runways, gare_loc)

                if runway:

                        # Remove aviao da lista de espera de descolagens
                        self.agent.takeoffQueue.remove(plane)
                        # print(f"Control tower removed plane {plane_jid} from the takeoff queue.")

                        # Adiciona à lista de aviões que estão a levantar
                        plane["runway"] = runway
                        self.agent.planesTakeoff.append(plane)

                        # Altera o estado da pista
                        self.agent.runways[runway]["status"] = "occupied"
                        # print(f"Runway {runway} occupied ...")
                        
                        # Envia a mensagem de confirmacao de descolagem ao aviao
                        data = {"runway": runway}
                        json_data = jsonpickle.encode(data)
                        plane_jid = str(plane["id"])
                        response_plane = Message(to=plane_jid)
                        response_plane.set_metadata("performative", "agree_takeoff")
                        response_plane.body = json_data
                        await self.send(response_plane)