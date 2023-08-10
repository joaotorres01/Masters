from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle


class TowerGiveInformationBehav(OneShotBehaviour):

    async def run(self):
        
        json_data = jsonpickle.encode({
            "landingQueue": self.agent.landingQueue,
            "takeoffQueue": self.agent.takeoffQueue,
            "planesLanding": self.agent.planesLanding,
            "planesTakeoff": self.agent.planesTakeoff
        })

        # Envia mensagem ao manager com as informacoes 
        response = Message(to="manager@" + XMPP_SERVER)
        response.set_metadata("performative", "response_information")
        response.body = json_data
        await self.send(response)
