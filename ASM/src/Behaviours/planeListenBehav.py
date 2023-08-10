from spade.behaviour import CyclicBehaviour
from Behaviours.planeLandingBehav import PlaneLandingBehav
from Behaviours.planeTakeoffBehav import PlaneTakeoffBehav
from Behaviours.planeTimeoutBehav import PlaneTimeoutBehav
import jsonpickle

class PlaneListenBehav(CyclicBehaviour):

    async def run(self):
        msg = await self.receive(timeout=1000)
        toDo = msg.get_metadata("performative")
        
        # Aterragem autorizada 
        if toDo == "agree_landing":
            # print(f"Plane {self.agent.jid} received: {toDo}")
            json_data = msg.body
            mensagem = jsonpickle.decode(json_data)

            a = PlaneLandingBehav(mensagem)
            self.agent.add_behaviour(a)

        # Descolagem autorizada
        elif toDo == "agree_takeoff":
            # print(f"Plane received: {toDo}")
            json_data = msg.body
            mensagem = jsonpickle.decode(json_data)

            a = PlaneTakeoffBehav(mensagem)
            self.agent.add_behaviour(a)

        # Aterragem nao autorizada
        elif toDo == "failure_landing":
            # print(f"Plane received: {toDo}")

            message = await self.receive(timeout=self.agent.waitTime)

            if message is None:
                a = PlaneTimeoutBehav()
                self.agent.add_behaviour(a)

            elif message.get_metadata("performative") == "agree_landing":
                # print(f"Plane {self.agent.jid} received: {toDo}")
                json_data = message.body
                message = jsonpickle.decode(json_data)

                a = PlaneLandingBehav(message)
                self.agent.add_behaviour(a)

            elif message.get_metadata("performative") == "agree_takeoff":
                # print(f"Plane received: {toDo}")
                json_data = message.body
                message = jsonpickle.decode(json_data)

                a = PlaneTakeoffBehav(message)
                self.agent.add_behaviour(a)

        # Descolagem nao autorizada
        elif toDo == "failure_takeoff":
            print(f"Plane {self.agent.jid} received: {toDo}. Plane added to the take off queue.")

        # Aterragem nao autorizada e fila de espera cheia
        elif toDo == "refuse":
            print(f"Plane {self.agent.jid} received: {toDo}. Finding another airport.")
            await self.agent.stop()
            