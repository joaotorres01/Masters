from spade.agent import Agent
from Behaviours.gareListenBehav import gareListenBehav

class GareAgent(Agent):

    async def setup(self):
        self.gares = {
                "g1":  {"location": (0   , 300), "type": "commercial", "status": "occupied"},
                "g2":  {"location": (50  , 300), "type": "cargo"     , "status": "occupied"},
                "g3":  {"location": (100 , 300), "type": "commercial", "status": "free"},
                "g4":  {"location": (150 , 300), "type": "cargo"     , "status": "free"},
                "g5":  {"location": (200 , 300), "type": "commercial", "status": "free"},
                "g6":  {"location": (250 , 300), "type": "cargo"     , "status": "free"},
                "g7":  {"location": (300 , 300), "type": "commercial", "status": "free"},
                "g8":  {"location": (350 , 300), "type": "cargo"     , "status": "free"},
                "g9":  {"location": (400 , 300), "type": "commercial", "status": "free"},
                "g10": {"location": (450 , 300), "type": "cargo"     , "status": "free"},
                "g11": {"location": (500 , 300), "type": "commercial", "status": "free"},
                "g12": {"location": (550 , 300), "type": "cargo"     , "status": "free"},
                "g13": {"location": (600 , 300), "type": "commercial", "status": "free"},
                "g14": {"location": (650 , 300), "type": "cargo"     , "status": "free"},
                "g15": {"location": (700 , 300), "type": "commercial", "status": "free"},
                "g16": {"location": (750 , 300), "type": "cargo"     , "status": "free"},
                "g17": {"location": (800 , 300), "type": "commercial", "status": "free"},
                "g18": {"location": (850 , 300), "type": "cargo"     , "status": "free"},
                "g19": {"location": (900 , 300), "type": "commercial", "status": "free"},
                "g20": {"location": (950 , 300), "type": "cargo"     , "status": "free"}
            }
        
        print("Gare Agent {}".format(str(self.jid)) + " starting...")
    
        a = gareListenBehav()
        self.add_behaviour(a)