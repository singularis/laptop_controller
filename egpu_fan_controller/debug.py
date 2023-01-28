import serial
import time
import GPUtil
from tkinter import messagebox

RELAY_1_CLOSE = [0xA0, 0x01, 0x01, 0xA2]
RELAY_1_OPEN = [0xA0, 0x01, 0x00, 0xA1]
RELAY_2_CLOSE = [0xA0, 0x02, 0x01, 0xA3]
RELAY_2_OPEN = [0xA0, 0x02, 0x00, 0xA2]
COOL_DOWN_TEMP = 70
PORT = 'COM3'
TEMP_DRIFT = 5
SAMPLE = 10


def error_popup(title, message):
    messagebox.showerror(title, message)


def gpu_init():
    return GPUtil.getGPUs()[0]


def gpu_checker():
    try:
        gpu_init()
        print("eGPU metrics successfully initialized")
    except ValueError:
        while True:
            print("No eGPU connected, waiting for eGPU ...")
            time.sleep(SAMPLE)
            gpu_checker()
            break
    except IndexError:
        error_popup("eGPU error", "Please check eGPU connected list")


def get_cpu_temp():
    gpu = gpu_init()
    return gpu.temperature


def serial_open():
    time.sleep(SAMPLE)
    try:
        return serial.Serial(
            port=PORT,
            baudrate=9600,
        )
    except serial.serialutil.SerialException:
        error_popup('Serial error', 'Please check relay connection')
        raise Exception("Relay not found on serial port")


def term_regulation():
    serial_handler = serial_open()
    try:
        while True:
            time.sleep(SAMPLE)
            cpu_temp = get_cpu_temp()
            print(cpu_temp)
            if cpu_temp > COOL_DOWN_TEMP:
                serial_handler.write(RELAY_1_CLOSE)
            if cpu_temp < COOL_DOWN_TEMP - TEMP_DRIFT:
                serial_handler.write(RELAY_1_OPEN)
    except Exception:
        serial_handler.close()
        gpu_checker()
        term_regulation()


if __name__ == '__main__':
    gpu_checker()
    term_regulation()
