import serial
import time

qr_reader = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

while True:
    qr_code = qr_reader.readline()
    if qr_code != '':
        exchange = open('serial.txt', 'w')
        exchange.write(qr_code)
        exchange.close()