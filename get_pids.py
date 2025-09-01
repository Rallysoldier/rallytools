import psutil
import time as _time
import sys

# Usage: python show_procs.py 5   # prints for 5 seconds ("time = n")
n = int(sys.argv[1]) if len(sys.argv) > 1 else 5

end = _time.time() + n
while _time.time() < end:
    for p in psutil.process_iter(['pid', 'name', 'exe', 'create_time']):
        try:
            print(p.info)  # same formatting as your original: {'pid':..., 'name':..., ...}
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    _time.sleep(1)
