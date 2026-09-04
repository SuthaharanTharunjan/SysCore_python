import psutil
print(psutil.cpu_freq(percpu=True))
print(psutil.sensors_temperatures(fahrenheit=False))