from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle

# Verifica se existe alguma pista disponível para um certo tipo de aviao e devolve um dicionario destas
def available_gares(gares, type):
    available = {}
    for key, value in gares.items():
        if value["type"] == type and value["status"] == "free":
            available[key] = value
    return available

class GareRequestBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    async def run(self):

        # Gares disponiveis
        free_gares = available_gares(self.agent.gares, self.data["type"])

        # Codifica o dicionario de gares disponiveis
        json_data = jsonpickle.encode(free_gares)
        
        # Manda as gares disponiveis para a torre de controlo
        response_list = Message(to="tower@" + XMPP_SERVER)
        response_list.set_metadata("performative", "inform")
        response_list.body = json_data
        # print(f"Gare manager sending control tower the free gares...")
        await self.send(response_list)

        # Espera resposta da torre de controlo
        gare_occupy = await self.receive(timeout=1000)
        toDo = gare_occupy.get_metadata("performative")
        # print(f"Gare manager received: {toDo}")

        if toDo == "request_occupy":

            json_data = gare_occupy.body
            gare = jsonpickle.decode(json_data)

            # Altera o estado da gare para ocupada
            self.agent.gares[gare]["status"] = "occupied"
            # print(f"Gare {gare} occupied ...")