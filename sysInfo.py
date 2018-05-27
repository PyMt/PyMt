import cpuinfo,monitor

CPUinfo = cpuinfo.CPUinfo()
for processor in CPUinfo.keys():
    cpu = {"cpuinfo":CPUinfo[processor]['model name']}
    print (cpu)

meminfo = monitor.meminfo()
memToal = {"memToal": 'Total memory: {0}'.format(meminfo['MemTotal'])}
memFree = {"memFree": 'Free memory: {0}'.format(meminfo['MemFree'])}
print (memToal)
print (memFree)

SysInfo = {"cpu", "memToal", "memFree"}
print (SysInfo)
