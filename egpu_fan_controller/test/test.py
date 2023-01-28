from threading import Thread
from serial import Serial
import time
import GPUtil
import subprocess
from tkinter import messagebox
import re

RELAY_1_CLOSE = [0xA0, 0x01, 0x01, 0xA2]
RELAY_1_OPEN = [0xA0, 0x01, 0x00, 0xA1]
RELAY_2_CLOSE = [0xA0, 0x02, 0x01, 0xA3]
RELAY_2_OPEN = [0xA0, 0x02, 0x00, 0xA2]
COOL_DOWN_TEMP = 70
PORT = 'COM3'
TEMP_DRIFT = 5
SAMPLE_TIME = 30


def error_popup(title, message):
    messagebox.showerror(title, message)


class SerialHandler(Serial):
    def __int__(self, port):
        super(SerialHandler, self).__init__()
        self.port = self.port
        self.baudrate = 9600

    def serial_open(self):
        try:
            self
        except self.serialutil.SerialException:
            error_popup('Serial error', 'Please check relay connection')
            raise Exception("Relay not found on serial port")

    def serial_close(self):
        self.close()


def connection_wait():
    monitor.stop()
    serial_relay.serial_close()
    monitor.gpu_checker()
    serial_relay.serial_open()


def get_gpus():
    gpu_list = (subprocess.run(["powershell", "-Command", 'wmic path win32_VideoController get name'],
                               capture_output=True))
    if re.search(".*NVIDIA GeForce GTX 1080.*", str(gpu_list)):
        print("True")
    else:
        print("False")


class Monitor(Thread):
    def __init__(self, delay):
        super(Monitor, self).__init__()
        self.stopped = False
        self.delay = delay  # Time between calls to GPUtil

    def gpu_init(self):
        return GPUtil.getGPUs()[0]

    def get_cpu_temp(self):
        gpu = self.gpu_init()
        return gpu.temperature

    def gpu_checker(self):
        try:
            self.gpu_init()
            print("eGPU metrics successfully initialized")
        except ValueError:
            while True:
                print("No eGPU connected, waiting for eGPU ...")
                time.sleep(SAMPLE_TIME)
                self.gpu_checker()
                break
        except IndexError:
            error_popup("eGPU error", "Please check eGPU connected list")

    def run(self):
        try:
            serial_relay.serial_open()
            while not self.stopped:
                gpu_temp = self.get_cpu_temp()
                time.sleep(SAMPLE_TIME)
                print(gpu_temp)
                if gpu_temp > COOL_DOWN_TEMP:
                    serial_relay.write(RELAY_1_CLOSE)
                if gpu_temp < COOL_DOWN_TEMP - TEMP_DRIFT:
                    serial_relay.write(RELAY_1_OPEN)
        except Exception:
            connection_wait()

    def stop(self):
        print("stopped")
        self.stopped = True


# Instantiate monitor with a 10-second delay between updates
get_gpus()
serial_relay = SerialHandler(PORT)
monitor = Monitor(SAMPLE_TIME)

monitor.start()
