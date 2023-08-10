from spade.behaviour import OneShotBehaviour

class TowerTimeoutBehav(OneShotBehaviour):

    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data

    # Receber id e retira aviao da landing queue
    async def run(self):

        for plane in self.agent.landingQueue:
            if str(plane["id"]) == str(self.data):
                self.agent.landingQueue.remove(plane)
                # print(f"Control tower removed plane {self.data} from the landing queue.")