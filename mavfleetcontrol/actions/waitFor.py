from MAVFleetControl.mavfleetcontrol.craft import Craft
from MAVFleetControl.mavfleetcontrol.craft import State
from  MAVFleetControl.mavfleetcontrol.actions.emergency import Emergency
import geopy.distance
import asyncio


class WaitFor:
    """
        Class responsible for waiting for an ambulance to reach a drones position
    """
    def __init__(self, ambulance, drones, all_drones):
        self.ambulance = ambulance
        self.drones = drones
        self.all_drones = all_drones

    def dist(self, a, b):
        return geopy.distance.distance((a.lat, a.lng), (b.lat, b.lng)).m

    async def __call__(self, drone: Craft):
        drone.state = State.Wait # change state
        print("WaitFor")
        while True:
            if not drone.conn.telemetry.health_all_ok:
                print("-- drone ", drone.id, " is having issues aborting")
                drone.tasking.empty() # empty event loop
                drone.add_action(Emergency())
                break
            
            # test drones
            for other_drone in self.all_drones:
                # test that it is not the drone it self
                if not drone.id == other_drone.id and not drone.mission_id == other_drone.mission_id and drone.state is State.Wait: # drone need to be waiting to be pusheds
                    # test distance
                    if self.dist(drone.position, other_drone.position) < 5.0:
                        break # next waypoint pushed off the pin

            # test ambulances
            if self.dist(drone.position, self.ambulance.position) > 5.0:
                print("WaitFor dist: ", self.dist(drone.position, self.ambulance.position))
                await asyncio.sleep(2) # sleep for 0.2 second
            else:
                drone.state = State.Travel
                break
                
