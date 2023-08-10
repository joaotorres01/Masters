from spade.behaviour import CyclicBehaviour
from Behaviours.gareRequestBehav import GareRequestBehav
from Behaviours.gareLocationBehav import GareLocationBehav
import jsonpickle

class gareListenBehav(CyclicBehaviour):

    async def run(self):
        
        # Recebe a mensagem
        msg = await self.receive(timeout=1000)
        toDo = msg.get_metadata("performative")

        # Recebe pedido da torre de controlo a pedir as gares livres
        if toDo == "request":

            # print(f"Gare manager received: {toDo}")
            json_data = msg.body
            plane_info = jsonpickle.decode(json_data)

            a = GareRequestBehav(plane_info)
            self.agent.add_behaviour(a)


        # Recebe pedido da torre de controlo a pedir a localizacao da gare
        elif toDo == "request_location":

            # print(f"Gare manager received: {toDo}")
            json_data = msg.body
            plane_info = jsonpickle.decode(json_data)

            a = GareLocationBehav(plane_info)
            self.agent.add_behaviour(a)