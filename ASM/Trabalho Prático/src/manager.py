from spade.agent import Agent
from Behaviours.managerRequestBehav import ManagerRequestBehav

class ManagerAgent(Agent):
    
    async def setup(self):
        print("Manager Agent {}".format(str(self.jid)) + " starting...")

        self.landingQueue = []
        self.takeoffQueue = []
        self.planesLanding = []
        self.planesTakeoff = []

        a = ManagerRequestBehav(period=10.0)
        self.add_behaviour(a)   