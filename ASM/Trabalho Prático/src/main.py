from plane import PlaneAgent
from tower import TowerAgent
from gare import GareAgent
from manager import ManagerAgent
import time
from dados import XMPP_SERVER, PASSWORD

if __name__ == "__main__":

    tower = TowerAgent("tower@" + XMPP_SERVER, PASSWORD)
    gare = GareAgent("gare@" + XMPP_SERVER, PASSWORD)
    manager = ManagerAgent("manager@" + XMPP_SERVER, PASSWORD)

    plane1 = PlaneAgent("g1", "plane1@" + XMPP_SERVER, PASSWORD)
    plane2 = PlaneAgent("g2", "plane2@" + XMPP_SERVER, PASSWORD)
    plane3 = PlaneAgent(None, "plane3@" + XMPP_SERVER, PASSWORD)
    plane4 = PlaneAgent(None, "plane4@" + XMPP_SERVER, PASSWORD)

    
    count = 5

    future = gare.start()
    future.wait()

    future = tower.start()
    future.wait()

    future = manager.start()
    future.wait()

    future = plane1.start()
    future.wait()

    future = plane2.start()
    future.wait()

    future = plane3.start()
    future.wait()

    future = plane4.start()
    future.wait()

    while True:

        plane = PlaneAgent(None, "plane" + str(count) + "@" + XMPP_SERVER, PASSWORD)
        future = plane.start()
        future.wait()
        count += 1;
        
        time.sleep(10)