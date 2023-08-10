from spade.behaviour import OneShotBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle
import asyncio

class PlaneTakeoffBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    async def run(self):

        # Altera a pista e o estado do aviao
        self.agent.runway = self.data["runway"]
        self.agent.state = "ground"

        # Aviao a ir da gare para a pista
        # print(f"Plane {str(self.agent.jid)} going from gare {str(self.agent.gare)} to runway {str(self.agent.runway)}.")
        self.agent.gare = None
        await asyncio.sleep(self.agent.moveTime)

        # Espera o tempo que fica na pista
        # print(f"Plane {str(self.agent.jid)} is taking off in runway {str(self.agent.runway)}")
        await asyncio.sleep(self.agent.runwayTime)

        # Envia mensagem à torre de controlo para desocupar a pista
        response = Message(to="tower@" + XMPP_SERVER)
        response.set_metadata("performative", "request_free")
        json_data = jsonpickle.encode(self.agent.runway)
        response.body = json_data
        await self.send(response)
        # print(f"Plane {str(self.agent.jid)} took off. Indicating control tower that the runway {str(self.agent.runway)} is free...")
        
        self.agent.state = "air"

        await self.agent.stop()
        # print(f"Plane {str(self.agent.jid)} has left the airport.")

        # Envia mensagem à torre de controlo para desocupar a pista
        json_data = jsonpickle.encode(str(self.agent.jid))

        response = Message(to="tower@" + XMPP_SERVER)
        response.set_metadata("performative", "inform_takeoff")
        response.body = json_data
        await self.send(response)