from spade.agent import Agent
from Behaviours.planeListenBehav import PlaneListenBehav
from Behaviours.landingRequestBehav import LandingRequestBehav
from Behaviours.takeoffRequestBehav import TakeoffRequestBehav
import random

class PlaneAgent(Agent):

    def __init__(self, start_gare, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_gare = start_gare

    async def setup(self):

        companies = ["RyanAir", "EasyJet", "TAP", "Emirates", "Qatar Airways", "Turkish Airlines", "Etihad Airways"]
        types = ["cargo", "commercial"]
        places = ["Porto", "Lisboa", "Madrid", "Barcelona", "Paris", "Marselha"]

        self.company = random.choice(companies)
        self.type = random.choice(types)
        self.runway = None

        # Tempo que demora a aterrar e que fica no aeroporto (podia ser random)
        self.waitTime = 15
        self.landingTime = 5
        self.runwayTime = 5
        self.moveTime = 5   

        if self.start_gare:
            self.state = "parked"
            self.origin = "Braga"
            self.destiny = random.choice(places)
            self.gare = self.start_gare

        else:
            self.state = "air"
            self.origin = random.choice(places)
            self.destiny = "Braga"
            self.gare = None

        print("Plane Agent {}".format(str(self.jid)) + " starting...")

        a = PlaneListenBehav()
        self.add_behaviour(a)

        if self.start_gare:

            b = TakeoffRequestBehav()
            self.add_behaviour(b)

        else:

            c = LandingRequestBehav()
            self.add_behaviour(c)