from .. import bluetooth
from queue import Queue
from threading import Thread
from typing import Union
import time
CHANNELS: Union[16, 8] = 16


class bt(Thread):
    def __init__(self, device_queue: Queue, duration=3):
        super().__init__(daemon=True)
        self.device_queue = device_queue
        self.duration = duration
        self.__search_flag = True
        self.validate_interface()

    def validate_interface(self):
        try:
            print([str(bluetooth.read_local_bdaddr())])
        except Exception:
            warn = "Bluetooth card disabled or not inserted, please enable it in system setting."
            raise Exception(warn)


    def run(self):
        added_devices = set()
        search_interval = 0
        start=time.time()
        while self.__search_flag:
            search_interval = min(search_interval + 1, 3)
            nearby_devices = bluetooth.discover_devices(
                lookup_names=True, duration=search_interval
            )
            for device in nearby_devices:
                addr = device[0]
                name = device[1]
                if CHANNELS == 16:
                    if "iRecorder-" not in name:
                        continue
                elif CHANNELS == 8:
                    if "iRecorder8-" not in name:
                        continue
                if name not in added_devices:
                    added_devices.add(name)
                    self.device_queue.put([name, addr, addr])
            if self.duration is None:
                continue
            if time.time()-start>self.duration:
                break

    def connect(self, addr):
        self.__search_flag = False
        uuid = "00001101-0000-1000-8000-00805f9b34fb"
        service_matches = bluetooth.find_service(uuid=uuid, address=addr)
        if len(service_matches) == 0:
            warn = "Bluetooth connection failed, please retry."
            self.device_queue.put(warn)
            raise Exception(warn)
        device = service_matches[0]
        return (device["host"], device["port"])
