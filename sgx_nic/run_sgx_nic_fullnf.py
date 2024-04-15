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
# cpus = ['timing', 'detailed']
cpus = ['detailed']
modes = ['none', 'tp']
# mem_size = '192GB'

million = 1000000
billion = 1000000000
trillion = 1000000000000
# once any nf reaches this number of ins, gem5 will enter real simulation. 
# acl-fw warmup: 400k->5 Trillion ticks->10billion ins
fast_forward_ins = 1 * million
final_ins = 4 * million # 2 * million

# fast_forward_ins = 10000
# final_ins = 1000000

# 1 * trillion: the benchmarking time.
final_ticks = 4 * billion

# --fast-forward=1000000000 \
# --maxinsts=1000000000 \
# --maxtick=2000000000000000 \

def bit_num(x):
    cnt = 0
    for i in range(32):
        if ((x >> i) & 1) == 1:
            cnt += 1
    return cnt        

multiprog = []
for i in nfinvoke:
    for j in nfinvoke:
        if i >= j: continue
        compliment_set = tuple(sorted(filter(lambda x: x != i and x != j, nfinvoke)))
        multiprog.append(compliment_set) # set of 4 NFs
        multiprog.append((*nfinvoke, i, j)) # set of 8 NFs
        multiprog.append((*nfinvoke, *nfinvoke, *compliment_set)) # set of 16 NFs

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

l2_size = ['4MB']
l2_pri_mapping = {
    '4MB': { 4: '1MB', 8: '512kB', 16: '256kB'}
}

all_commands = []

def gen_scripts():
    for cpu in cpus:
        for nf_set in multiprog:
            nf_set_len = len(nf_set)
            cmd = prog_set_to_cmd(nf_set)
            for l2 in l2_size:
                l2_pri = l2_pri_mapping[l2][nf_set_len]
                for mode in modes:
                    # baseline - none;
                    # time partitioning - tp
                    filename = f'{cpu}_{cmd}_{l2}_{mode}'
                    bash_filename = f'{scriptgen_dir}/run_{filename}.sh'
                    script = open(bash_filename, "w")
                    command = "#!/bin/bash\n"
                    command += "build/ARM/gem5.opt \\\n"
                    command += "    --remote-gdb-port=0 \\\n"
                    command += "    --outdir=/gem5/sgx_nic/m5out/" + filename + " \\\n"
                    command += "    --stats-file=" + filename + "_stats.txt \\\n"
                    command += "    configs/dramsim2/dramsim2_se.py \\\n"
                    command += "    --cpu-type=" + cpu + " --clock=2.4GHz \\\n"
                    command += "    --cacheline_size=128 \\\n"
                    command += "    --caches --l2cache \\\n"
                    if mode == 'tp':  
                        command += "    --l2config=setpartition \\\n"
                        command += "    --l2_size=" + l2_pri + " --l2_assoc=16 \\\n"
                    else:
                        command += "    --l2config=shared \\\n"
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
                    for i, w in enumerate(nf_set):
                        command += f"    --p{i}=/NFShield/{w} \\\n"
                    command += "    > " + results_dir + "/stdout_" + filename + ".out \\\n"
                    command += "    2> " + stderr_dir + "/stderr_" + filename + ".out"
                    script.write(f'{command}\n')
                    script.close()
                    os.system(f'chmod +x {bash_filename}')
                    # os.system(f'bash {bash_filename}')
                    all_commands.append(f'bash {bash_filename}')

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
    pool = ThreadPool(4)
    results = pool.map(exe_gem5_sim, commands)
    pool.close()
    pool.join()
    for res in results:
        print(res)

if __name__ == "__main__":
    gen_scripts()
    num_cmd = len(all_commands)
    print(f'The number of gem5 simulations is {num_cmd}')
    # num_par = int(num_cmd / 4)
    # run_gem5_sim(all_commands[0:64])
    # run_gem5_sim(all_commands[num_par:num_par * 2])
    # run_gem5_sim(all_commands[num_par * 2:num_par * 3])
    # run_gem5_sim(all_commands[num_par * 3:])
