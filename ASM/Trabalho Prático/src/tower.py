from spade.agent import Agent
from Behaviours.towerListenBehav import towerListenBehav

class TowerAgent(Agent):
    
    async def setup(self):
        print("Tower Agent {}".format(str(self.jid)) + " starting...")
    
        self.landingQueue = []
        self.maxQueueSize = 10

        self.takeoffQueue = []

        self.planesLanding = []
        self.planesTakeoff = []
        
        self.runways = {
            "r1": {"location": (400, 400), "status": "free"},
            "r2": {"location": (600, 400), "status": "free"},
            "r3": {"location": (600, 600), "status": "free"},
            "r4": {"location": (400, 600), "status": "free"}
        }
        
        a = towerListenBehav()
        self.add_behaviour(a)