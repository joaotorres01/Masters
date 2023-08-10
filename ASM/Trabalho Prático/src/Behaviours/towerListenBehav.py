from spade.behaviour import CyclicBehaviour
from Behaviours.towerLandingBehav import TowerLandingBehav
from Behaviours.towerTakeoffBehav import TowerTakeoffBehav
from Behaviours.towerFreeRunwayBehav import TowerFreeRunwayBehav
from Behaviours.towerTimeoutBehav import TowerTimeoutBehav
from Behaviours.towerGiveInformationBehav import TowerGiveInformationBehav
import jsonpickle


class towerListenBehav(CyclicBehaviour):

    async def run(self):
        # Recebe a mensagem
        msg = await self.receive(timeout=1000)
        toDo = msg.get_metadata("performative")
        

        # Recebe pedido de aviao a querer aterrar
        if toDo == "request_landing":
            # print(f"Control Tower received: {toDo}")

            # processa a mensagem e verifica se há espaço disponível para aterrar
            # print(f"Landing request received from {msg.sender}. Aircraft: {msg.body}")
            json_data = msg.body
            plane_info = jsonpickle.decode(json_data)

            a = TowerLandingBehav(plane_info)
            self.agent.add_behaviour(a)

        # Recebe pedido de aviao a querer levantar voo
        elif toDo == "request_takeoff":
            # print(f"Control Tower received: {toDo}")
            
            # Processa a mensagem e verifica se ha espaço disponivel para levantar voo
            # print(f"Takeoff request received from {msg.sender}. Aircraft: {msg.body}")
            json_data = msg.body
            plane_info = jsonpickle.decode(json_data)

            a = TowerTakeoffBehav(plane_info)
            self.agent.add_behaviour(a)

        # Recebe pedido de aviao para esvaziar a pista
        elif toDo == "request_free":
            # print(f"Control Tower received: {toDo}")

            # Processa a mensagem e verifica se ha espaço disponivel para levantar voo
            # print(f"Free runway request received from {msg.sender}. Runway: {msg.body}")
            json_data = msg.body
            runway = jsonpickle.decode(json_data)

            a = TowerFreeRunwayBehav(runway)
            self.agent.add_behaviour(a)
        
        # Recebe pedido de aviao a dizer esperou o tempo maximo na fila de espera
        elif toDo == "cancel":
            # print(f"Control Tower received: {toDo}")

            # print(f"Time out request received from {msg.sender}.")
            json_data = msg.body
            id = jsonpickle.decode(json_data)

            a = TowerTimeoutBehav(id)
            self.agent.add_behaviour(a)

        # Recebe pedido para dar display das informações
        elif toDo == "request_information":
            # print(f"Control Tower received: {toDo}")

            # print(f"Information request received from manager.")
            
            a = TowerGiveInformationBehav()
            self.agent.add_behaviour(a)   

        # Remover aviao da lista de avioes a aterrar
        elif toDo == "inform_landing":
            # print(f"Control Tower received: {toDo}")
            # print("Update the list of planes landing...")
            json_data = msg.body
            plane_jid = jsonpickle.decode(json_data)

            # Remove aviao da lista das aterragens
            for plane in self.agent.planesLanding:
                if plane["id"] == plane_jid:
                    self.agent.planesLanding.remove(plane)
                    # print(f"Control tower removed plane {plane_jid} from the planes landing list.")
            
        # Remover aviao da lista de avioes a descolar
        elif toDo == "inform_takeoff":
            # print(f"Control Tower received: {toDo}")
            # print("Update the list of planes taking off...")
            json_data = msg.body
            plane = jsonpickle.decode(json_data)

            # Remove aviao da lista das descolagens
            for plane in self.agent.planesTakeoff:
                if plane["id"] == str(msg.sender):
                    self.agent.planesTakeoff.remove(plane)
                    # print(f"Control tower removed plane {msg.sender} from the planes taking off list.")

            


            
