import m5
from m5.objects import *
import sys

#Setting L1 Cache System
class L1Cache(Cache):
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    
class L1ICache(L1Cache):
    size = '16kB'

class L1DCache(L1Cache):
    size = '64kB'
 
#Create the system for our architecture simulation
system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

#Simple CPU and Memory Config
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('8192MB')]
system.cpu = TimingSimpleCPU()
system.membus = SystemXBar()

#Memory Control
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

#Creating a Simple L1 Cache System
system.cpu.icache = L1ICache()  # L1 Instruction Cache
system.cpu.dcache = L1DCache()  # L1 Data Cache


#Connecting CPU and Cache with iCache and dCache ports
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

#Connecting L1 Cache to membus
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

#This specific interrupts is required for X86 processor
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports

#Taking input from command line for binary file
binary = sys.argv[sys.argv.index('-c') + 1]

# Create a process for the provided binary
# And create a workload
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()
system.workload = SEWorkload.init_compatible(binary)

#Simulation Configuration
root = Root(full_system=False, system=system)
m5.instantiate()
print("Beginning of the Simulation!!!!")
exit_event = m5.simulate()
print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
