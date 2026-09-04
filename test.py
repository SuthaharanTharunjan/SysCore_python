import psutil
print(psutil.cpu_freq(percpu=True))

print(psutil.virtual_memory().percent)