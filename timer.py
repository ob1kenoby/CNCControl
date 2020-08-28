from datetime import datetime
import time
import sys

work_until = datetime.strptime(sys.argv[1], '%Y-%m-%dT%H:%M:%S')
while True:
    if datetime.now() > work_until:
        break
    time.sleep(5)