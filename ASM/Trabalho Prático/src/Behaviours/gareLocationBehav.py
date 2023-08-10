from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle

class GareLocationBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    async def run(self):

        # Vai buscar a localizacao da gare
        gare_location = self.agent.gares[self.data["gare"]]["location"]

        # Libertar a gare
        self.agent.gares[self.data["gare"]]["status"] = "free"

        # Envia a localizacao da gare para a torre de controlo
        json_data = jsonpickle.encode(gare_location)
        response = Message(to="tower@" + XMPP_SERVER)
        response.set_metadata("performative", "inform_location")
        response.body = json_data
        # print(f"Gare manager sent gare location to control tower and freed the gare.")
        await self.send(response)