#
# Created by Renatus Madrigal on 02/14/2025
#

from pymobiledevice3.usbmux import list_devices
from pymobiledevice3.lockdown import create_using_usbmux, LockdownServiceProvider
from pymobiledevice3.services.amfi import AmfiService
from pymobiledevice3.remote.tunnel_service import start_tunnel, CoreDeviceTunnelProxy, TunnelProtocol
from pymobiledevice3.remote.remote_service_discovery import RemoteServiceDiscoveryService
from pymobiledevice3.services.dvt.dvt_secure_socket_proxy import DvtSecureSocketProxyService
from pymobiledevice3.services.dvt.instruments.location_simulation import LocationSimulation
from pymobiledevice3.exceptions import InvalidServiceError
from multiprocessing import Queue
from .util import thread_with_future, async_run_in_thread
import traceback
import sys
import asyncio


class DeviceManager:

    @staticmethod
    def get_devices_info():
        connected_devices = []
        for device in list_devices():
            udid = device.serial
            lockdown = create_using_usbmux(udid, autopair=False)
            connected_devices.append(lockdown.short_info)
        return connected_devices

    pass


class Device:

    def __init__(self, udid: str):
        self.udid = udid
        self.lockdown = create_using_usbmux(udid)
        self.name = self.lockdown.short_info.get('DeviceName', 'Unknown')
        self.service_provider: LockdownServiceProvider = self.lockdown
        self._queue = Queue()

    def password_protected(self) -> bool:
        return self.lockdown.all_values.get('PasswordProtected', False)

    def get_device_name(self) -> str:
        return self.lockdown.short_info.get('DeviceName', 'Unknown')

    def get_developer_status(self) -> bool:
        return self.lockdown.developer_mode_status

    def enable_developer_mode(self):
        AmfiService(self.lockdown).enable_developer_mode()

    def reveal_developer_options(self):
        AmfiService(self.lockdown).reveal_developer_mode_option_in_ui()

    async def start_tunnel_exec(self):
        # TODO: Try to move the CoreDeviceTunnelProxy to synchronous context
        try:
            service = CoreDeviceTunnelProxy(self.lockdown)
            async with start_tunnel(service, protocol=TunnelProtocol.TCP) as res:
                print("Tunnel started")
                self._queue.put((res.address, res.port))
                await res.client.wait_closed()
                print("Tunnel closed")
        except asyncio.CancelledError:
            print("Tunnel was closed by asyncio")

    def start_tunnel(self):
        @thread_with_future(name=f"{self.name}-Tunnel")
        async def _start_tunnel():
            await self.start_tunnel_exec()

        future = _start_tunnel()
        conn = self._queue.get()
        print("Got connection:", conn)
        try:
            self.set_rsd(conn)
        except Exception as ex:
            print(f"Exception occurred! {ex}")
            traceback.print_exc()
        finally:
            return future

    def set_rsd(self, conn: tuple[str, int]):
        rsd = RemoteServiceDiscoveryService(conn)
        asyncio.run(rsd.connect(), debug=True)
        self.service_provider = rsd

    def clear_location(self):
        with DvtSecureSocketProxyService(self.service_provider) as dvt:
            LocationSimulation(dvt).clear()

    def set_location(self, latitude: float, longitude: float):
        with DvtSecureSocketProxyService(self.service_provider) as dvt:
            LocationSimulation(dvt).set(latitude, longitude)
