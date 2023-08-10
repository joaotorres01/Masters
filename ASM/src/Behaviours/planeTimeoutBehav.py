from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle

class PlaneTimeoutBehav(OneShotBehaviour):

    async def run(self):

        # Envia mensagem a torre a dizer que quer sair da lista de espera e vai para outro aeroporto
        msg = Message(to="tower@" + XMPP_SERVER)
        msg.set_metadata("performative", "cancel")
        info = self.agent.jid
        msg.body = jsonpickle.encode(info)
        await self.send(msg)
        print(f"Plane {str(self.agent.jid)} reached their max wait time. Leaving the airport.")

        await self.agent.stop()