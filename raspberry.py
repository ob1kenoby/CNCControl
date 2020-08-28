from datetime import datetime
from contextlib import closing
import requests
import RPi.GPIO as GPIO
import subprocess
import time
import shutil
import urllib.request as request
import config as cfg


def enable_tool():
    """
    Активирует релейный выход 1 на устройстве если устройство не
    оборудовано ЧПУ, активирует и деактивирует выход, если устройство
    оборудовано ЧПУ. Возвращает предполагаемое состояние станка.
    """
    GPIO.output(relay_1_GPIO, GPIO.HIGH)
    if cfg.cfg['cnc']:
        time.sleep(0.5)
        GPIO.output(relay_1_GPIO, GPIO.LOW)
    return True


def disable_tool(order_no):
    """
    В качестве аргумента принимает номер задания. Деактивирует релейный
    выход 1, если устройство не оборудовано ЧПУ. Завершает отсчёт
    времени и возвращает предполагаемое состояние станка.
    :param order_no:
    :return:
    """
    if not cfg.cfg['cnc']:
        GPIO.output(relay_1_GPIO, GPIO.LOW)
    countdown.terminate()
    close_order = requests.post(stopURL, json={
            "deviceNo": cfg.cfg["deviceNo"],
            "order": order_no,
            "time": datetime.today().isoformat()
        })
    if not close_order.json()['ok']:
        req_time = close_order.json()['time']    # request time
        trace(f"Error occurred at closing order {order_no} at {req_time}")
    return False


def start_timer(work_until):
    return subprocess.Popen(["python", "timer.py", work_until])


def trace(message):
    print(f"{datetime.today().isoformat()} {message}")


def read_id():
    exchange = open('serial.txt', 'rw')
    auth_id = exchange.readline()
    exchange.write('')
    exchange.close()
    return auth_id


isEnabled = False
lastID = ''
order = ''
ip = cfg.cfg["ipAddress"]
ftp_user = cfg.cfg["ftp_user"]
ftp_pass = cfg.cfg["ftp_password"]
cnc_share = r"\\" + cfg.cfg["cnc_ip"]
device_no = cfg.cfg["deviceNo"]
cnc = cfg.cfg["cnc"]

if cfg.cfg["https"]:
    connectionURL = f"https://{ip}:{cfg.cfg['port']}"
else:
    connectionURL = f"http://{ip}:{cfg.cfg['port']}"
stopURL = connectionURL + "/order_done"
connectionURL += "/access"

relay_1_GPIO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(relay_1_GPIO, GPIO.OUT)

qr_reader = subprocess.Popen(["python", "reader.py"])
while True:
    authorizationID = read_id()
    if isEnabled:
        if countdown.poll() == 0 or authorizationID == lastID:
            isEnabled = disable_tool(order)
            trace(f"Execution of the order {order} has ended")
    elif authorizationID != '':
        response = requests.post(connectionURL, json={
            "deviceNo": device_no,
            "authorizationID": authorizationID,
            "time": datetime.today().isoformat()
        })
        if response.json()['ok']:
            lastID, authorizationID = authorizationID, ''
            order = response.json()['order']
            if cnc:
                file = response.json('cnc')
                with closing(
                        request.urlopen(f"ftp://{ftp_user}:{ftp_pass}@{ip}/{file}")
                ) as r:
                    shutil.copyfile(r, f"{cnc_share}\\{file}")
                trace(f"The program {file} is uploaded")
                while True:
                    time.sleep(5)
                    if read_id() == lastID:
                        isEnabled = enable_tool()
                        countdown = start_timer(response.json()['timedelta'][:19])
                        trace(f"Execute order {order}")
                        break
            else:
                isEnabled = enable_tool()
                countdown = start_timer(response.json()['timedelta'][:19])
                trace(f"Access to the machine to execute order {order} is allowed")
    time.sleep(5)
