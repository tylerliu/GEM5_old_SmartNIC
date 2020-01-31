#!/usr/bin/python3.7

import os
import sys
from multiprocessing.dummy import Pool as ThreadPool
import threading

gem5home = os.getcwd()

scriptgen_dir = gem5home + "/scriptgen"
results_dir = gem5home + "/results"
stdout_dir = gem5home + "/stdout"
stderr_dir = gem5home + "/stderr"

nfinvoke = ['acl-fw', 'dpi', 'nat-tcp-v4', 'maglev', 'lpm', 'monitoring']
cpus = ['timing', 'detailed']
modes = ['none', 'tp']
# mem_size = '192GB'

million = 1000000
billion = 1000000000
trillion = 1000000000000
# once any nf reaches this number of ins, gem5 will enter real simulation. 
# acl-fw warmup: 400k->5 Trillion ticks->10billion ins
fast_forward_ins = 2 * billion
final_ins = 100 * million

# fast_forward_ins = 10000
# final_ins = 1000000

# 1 * trillion: the benchmarking time.
final_ticks = 2 * trillion

# --fast-forward=1000000000 \
# --maxinsts=1000000000 \
# --maxtick=2000000000000000 \

def bit_num(x):
    cnt = 0
    for i in range(32):
        if ((x >> i) & 1) == 1:
            cnt += 1
    return cnt        

singleprog = nfinvoke
multiprog = []
for i in range(1, 1 << 6):
    prog_set = []
    bitn = bit_num(i)
    if bitn not in [2, 4]:
        continue
    for j in range(6):
        if (i >> j) & 1 == 1:
            prog_set.append(nfinvoke[j])
    multiprog.append(prog_set)
multiprog = list(filter(lambda x: len(x) > 1, multiprog))
# print(multiprog, len(multiprog))

def prog_set_to_cmd(prog_set):
    ret = ''
    num_prog = len(prog_set)
    for i in range(num_prog - 1):
        ret += prog_set[i] + '.'
    ret += prog_set[-1]
    return ret

if not os.path.exists(scriptgen_dir):
    os.makedirs(scriptgen_dir)

if not os.path.exists(results_dir):
    os.makedirs(results_dir)

if not os.path.exists(stdout_dir):
    os.makedirs(stdout_dir)

if not os.path.exists(stderr_dir):
    os.makedirs(stderr_dir)

l2_size = ['4MB', '2MB', '1MB', '512kB', '256kB']

all_commands = []

def cache_partition():
    for cpu in cpus:
        for nf in singleprog:
            cmd = nf
            for l2 in l2_size:
                for mode in modes:
                    # baseline - none;
                    # time partitioning - tp
                    filename = f'{cpu}_{cmd}_{l2}_{mode}'
                    bash_filename = f'{scriptgen_dir}/run_{filename}.sh'
                    script = open(bash_filename, "w")
                    command = "#!/bin/bash\n"
                    command += "build/ARM/gem5.fast \\\n"
                    command += "    --remote-gdb-port=0 \\\n"
                    command += "    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/" + filename + " \\\n"
                    command += "    --stats-file=" + filename + "_stats.txt \\\n"
                    command += "    configs/dramsim2/dramsim2_se.py \\\n"
                    command += "    --cpu-type=" + cpu + " --clock=2.4GHz \\\n"
                    command += "    --cacheline_size=128 \\\n"
                    command += "    --caches --l2cache \\\n"
                    command += "    --l2_size=" + l2 + " --l2_assoc=16 \\\n"
                    if mode == 'tp':
                        command += "    --fixaddr \\\n"
                        command += "    --rr_nc \\\n"
                        command += "    --split_mshr \\\n"
                        command += "    --split_rport \\\n"
                    command += "    --dramsim2 \\\n"
                    command += "    --tpturnlength=6 \\\n"
                    command += "    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \\\n"
                    command += "    --systemcfg=./ext/DRAMSim2/system_" + mode + ".ini \\\n"
                    command += "    --outputfile=/dev/null \\\n"
                    command += "    --fast-forward=" + str(fast_forward_ins) + " \\\n"    
                    command += "    --maxinsts=" + str(final_ins) +  " \\\n"
                    command += "    --maxtick=" + str(final_ticks) + " \\\n"
                    command += "    --numpids=1 \\\n"
                    command += "    --p0=/users/yangzhou/NF-GEM5/" + cmd + " \\\n"
                    command += "    > " + results_dir + "/stdout_" + filename + ".out \\\n"
                    command += "    2> " + stderr_dir + "/stderr_" + filename + ".out"
                    script.write(f'{command}\n')
                    script.close()
                    os.system(f'chmod +x {bash_filename}')
                    # os.system(f'bash {bash_filename}')
                    all_commands.append(f'cd .. && bash {bash_filename}')

def bus_arbitor():
    for cpu in cpus:
        for nf_set in multiprog:
            nf_set_len = len(nf_set)
            cmd = prog_set_to_cmd(nf_set)
            l2 = '4MB'
            if nf_set_len == 2:
                l2 = '2MB'
            if nf_set_len == 4:
                l2 = '1MB'
            for mode in modes:
                # baseline - none;
                # time partitioning - tp
                filename = f'{cpu}_{cmd}_{l2}_{mode}'
                bash_filename = f'{scriptgen_dir}/run_{filename}.sh'
                script = open(bash_filename, "w")
                command = "#!/bin/bash\n"
                command += "build/ARM/gem5.fast \\\n"
                command += "    --remote-gdb-port=0 \\\n"
                command += "    --outdir=/users/yangzhou/GEM5_DRAMSim2/sgx_nic/m5out/" + filename + " \\\n"
                command += "    --stats-file=" + filename + "_stats.txt \\\n"
                command += "    configs/dramsim2/dramsim2_se.py \\\n"
                command += "    --cpu-type=" + cpu + " --clock=2.4GHz \\\n"
                command += "    --cacheline_size=128 \\\n"
                command += "    --caches --l2cache \\\n"
                command += "    --l2_size=" + l2 + " --l2_assoc=16 \\\n"
                if mode == 'tp':                        
                    command += "    --fixaddr \\\n"
                    command += "    --rr_nc \\\n"
                    command += "    --split_mshr \\\n"
                    command += "    --split_rport \\\n"
                command += "    --dramsim2 \\\n"
                command += "    --tpturnlength=6 \\\n"
                command += "    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \\\n"
                command += "    --systemcfg=./ext/DRAMSim2/system_" + mode + ".ini \\\n"
                command += "    --outputfile=/dev/null \\\n"
                command += "    --fast-forward=" + str(fast_forward_ins) + " \\\n"    
                command += "    --maxinsts=" + str(final_ins) +  "\\\n"
                command += "    --maxtick=" + str(final_ticks) + " \\\n"
                command += "    --numpids=" + str(nf_set_len) + " \\\n"
                command += "    --p0=/users/yangzhou/NF-GEM5/" + nf_set[0] + " \\\n"
                if nf_set_len >= 2:
                    command += "    --p1=/users/yangzhou/NF-GEM5/" + nf_set[1] + " \\\n"
                if nf_set_len >= 4:
                    command += "    --p2=/users/yangzhou/NF-GEM5/" + nf_set[2] + " \\\n"
                    command += "    --p3=/users/yangzhou/NF-GEM5/" + nf_set[3] + " \\\n"
                command += "    > " + results_dir + "/stdout_" + filename + ".out \\\n"
                command += "    2> " + stderr_dir + "/stderr_" + filename + ".out"
                script.write(f'{command}\n')
                script.close()
                os.system(f'chmod +x {bash_filename}')
                # os.system(f'bash {bash_filename}')
                all_commands.append(f'cd .. && bash {bash_filename}')

def exe_gem5_sim(cmd_line):
    try:
        print(f'{threading.currentThread().getName()} running: {cmd_line}', flush=True)
        os.popen(cmd_line).read()
        print(f'{threading.currentThread().getName()} okay: {cmd_line}', flush=True)
        return f'okay: {cmd_line}'
    except Exception:
        print(f'{threading.currentThread().getName()} fails: {cmd_line}', flush=True)
        return f'fails: {cmd_line}'

def run_gem5_sim(commands):
    # 1 thread is left.
    pool = ThreadPool(55)
    results = pool.map(exe_gem5_sim, commands)
    pool.close()
    pool.join()
    for res in results:
        print(res)

if __name__ == "__main__":
    cache_partition()
    bus_arbitor()
    num_cmd = len(all_commands)
    print(f'The number of gem5 simulations is {num_cmd}')
    num_par = int(num_cmd / 6) + 1
    run_gem5_sim(all_commands[0:num_par])
    # run_gem5_sim(all_commands[num_par:num_par * 2])
    # run_gem5_sim(all_commands[num_par * 2:num_par * 3])
    # run_gem5_sim(all_commands[num_par * 3:num_par * 4])
    # run_gem5_sim(all_commands[num_par * 4:num_par * 5])
    # run_gem5_sim(all_commands[num_par * 5:])