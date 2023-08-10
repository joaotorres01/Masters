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

class TowerLandingBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    async def run(self):
        # Codifica os dados do aviao que enviou o pedido
        json_data = jsonpickle.encode(self.data)

        # Torre de controlo contacta o gestor de gares para verificar se existe uma gare livre
        request_gare = Message(to="gare@" + XMPP_SERVER)
        request_gare.set_metadata("performative", "request")
        request_gare.body = json_data
        # print(f"Control tower contacting gare manager to check if there are any available gares...")
        await self.send(request_gare)

        # Recebe a resposta do gestor de gares
        response_list = await self.receive(timeout=1000)
        toDo = response_list.get_metadata("performative")
        # print(f"Control tower received from gare manager: {toDo}")

        # Recebe a lista de gares do gestor de gares
        if toDo == "inform":
            
            json_data = response_list.body
            free_gares = jsonpickle.decode(json_data)

            # Se houver gares livres
            if free_gares:

                # Depois de confirmada a existencia de gares verifica se ha pistas livres para aterragem 
                if available_runway(self.agent.runways):

                    # Calcula o caminho mais curto das pistas e gares disponiveis
                    runway, gare = shortest_path(self.agent.runways, free_gares)
                    
                    if runway or gare:

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
                        jid_plane = str(self.data["id"])
                        response_plane = Message(to=jid_plane)
                        response_plane.set_metadata("performative", "agree_landing")
                        landing_info = {"runway": runway,
                                        "gare": gare}
                        
                        json_data = jsonpickle.encode(landing_info)
                        response_plane.body = json_data
                        # print(f"Control tower sending landing confirmation to {jid_plane}")
                        await self.send(response_plane)

                        # Atualiza a informação do avião e adiciona à lista de aviões que estão aterrar
                        self.data["runway"] = runway
                        self.data["gare"] = gare
                        self.agent.planesLanding.append(self.data)

                # Nao existem pistas livres
                else:

                    if self.agent.maxQueueSize > len(self.agent.landingQueue):

                        # Adiciona a lista de espera de aterragens
                        self.agent.landingQueue.append(self.data)

                        # Envia a mensagem ao aviao a dizer que nao ha pistas disponiveis e tera que aguardar
                        response = Message(to=str(self.data["id"]))
                        response.set_metadata("performative", "failure_landing")
                        response.body = "Landing not authorized. No runway available. Added to the landing queue."
                        await self.send(response)

                    else:

                        # Comunica ao aviao a impossibilidade de aterrar
                        response = Message(to=str(self.data["id"]))
                        response.set_metadata("performative", "refuse")
                        response.body = "Landing not authorized. Landing queue is full. Find another airport."
                        await self.send(response)

                
            # Se receber que nao existem gares
            else:

                # Envia a mensagem de negacao
                response = Message(to=str(self.data["id"]))
                response.set_metadata("performative", "refuse")
                response.body = "Landing not authorized. No parking available."
                # print("Control tower received that there are no free gares.")
                await self.send(response)