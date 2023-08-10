from spade.behaviour import PeriodicBehaviour
from spade.message import Message
from dados import XMPP_SERVER
import jsonpickle
from prettytable import PrettyTable


class ManagerRequestBehav(PeriodicBehaviour):

    def display_info(self):

        table = PrettyTable()
        table.field_names = ["ID", "Company", "Type", "Origin", "Destiny", "Gare", "Runway", "State"]

        # Lista de espera para aterrar
        for plane in self.agent.landingQueue:
            table.add_row([plane["id"], plane["company"], plane["type"], plane["origin"], plane["destiny"], plane["gare"], plane["runway"], "In landing queue"])

        # Aterragem em progresso
        for plane in self.agent.planesLanding:
            table.add_row([plane["id"], plane["company"], plane["type"], plane["origin"], plane["destiny"], plane["gare"], plane["runway"], "Landing"])

        # Lista de espera para descolar
        for plane in self.agent.takeoffQueue:
            table.add_row([plane["id"], plane["company"], plane["type"], plane["origin"], plane["destiny"], plane["gare"], plane["runway"], "In takeoff queue"])

        # Descolagem em progresso
        for plane in self.agent.planesTakeoff:
            table.add_row([plane["id"], plane["company"], plane["type"], plane["origin"], plane["destiny"], plane["gare"], plane["runway"], "Taking off"])

        print(table)

    async def run(self):
        
        # Cria a mensagem com as informacoes do voo
        msg = Message(to="tower@" + XMPP_SERVER)  # destinatário é a torre de controle
        msg.set_metadata("performative", "request_information")
        # print(f"Manager asking control tower for information...")
        await self.send(msg)

        # Recebe a mensagem
        message = await self.receive(timeout=1000)
        toDo = message.get_metadata("performative")

        if toDo == "response_information":

            data = jsonpickle.decode(message.body)
            self.agent.landingQueue = data["landingQueue"]
            self.agent.takeoffQueue = data["takeoffQueue"]
            self.agent.planesLanding = data["planesLanding"]
            self.agent.planesTakeoff = data["planesTakeoff"]
            self.display_info()
        else:
            print("ManagerAgent: Nenhuma mensagem recebida.")