#
# Created by Renatus Madrigal on 02/14/2025
#

from .device import Device, InvalidServiceError
from .route import Route
import random
import asyncio


async def run_loop(route: Route, device: Device, v=3.0, dt=0.2, sigma=1.0):
    run_v = random.normalvariate(v, sigma)
    route.generate_path(v=run_v, dt=dt)
    for point in route.run_path:
        device.set_location(point['lat'], point['lng'])
        await asyncio.sleep(dt)


async def run(route: Route, device: Device, loop_cnt: int = 5, v=3.0, dt=0.2, sigma=1.0):
    for i in range(loop_cnt):
        print(f"Running loop {i}")
        try:
            await run_loop(route, device, v, dt, sigma)
        except InvalidServiceError:
            print("Invalid Service in running loop")
        except KeyboardInterrupt:
            print("Keyboard Interrupt in running loop")
        finally:
            print("Clear location simulation")
            device.clear_location()
            raise
