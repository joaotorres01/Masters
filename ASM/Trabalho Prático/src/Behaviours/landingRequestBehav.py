from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle

class LandingRequestBehav(OneShotBehaviour):
    async def run(self):

        # Obtem informacoes do voo
        plane_info = {"id": str(self.agent.jid),
                      "state": self.agent.state,
                      "company": self.agent.company,
                      "type": self.agent.type,
                      "origin": self.agent.origin,
                      "destiny": self.agent.destiny,
                      "runway": self.agent.runway,
                      "gare": self.agent.gare,
                      "waitTime": str(self.agent.waitTime),
                      "landingTime": str(self.agent.landingTime),
                      "runwayTime": str(self.agent.runwayTime),
                      "moveTime": str(self.agent.moveTime)
                      }
        json_data = jsonpickle.encode(plane_info)

        # Cria a mensagem com as informacoes do voo
        msg = Message(to="tower@" + XMPP_SERVER)  # destinatário é a torre de controle
        msg.set_metadata("performative", "request_landing")
        msg.body = json_data
        print(f"Plane {str(self.agent.jid)} requesting to land")
        
        # Envia a mensagem
        await self.send(msg)