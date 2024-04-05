#!/bin/bash
build/ARM/gem5.opt \
    --remote-gdb-port=0 \
    --outdir=/GEM5_DRAMSim2/sgx_nic/m5out/test_none \
    --stats-file=test_none_stats.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed --clock=2.4GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2config=shared \
    --l2_size=4MB --l2_assoc=16 \
    --dramsim2 \
    --tpturnlength=6 \
    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
    --systemcfg=./ext/DRAMSim2/system_none.ini \
    --outputfile=/dev/null \
    --fast-forward=750000000 \
    --maxinsts=1000000\
    --maxtick=2000000000000 \
    --numpids=16 \
    --p0=/NFShield/nat-tcp-v4 \
    --p1=/NFShield/maglev \
    --p2=/NFShield/lpm \
    --p3=/NFShield/monitoring \
    --p4=/NFShield/acl-fw \
    --p5=/NFShield/dpi \
    --p6=/NFShield/lpm \
    --p7=/NFShield/monitoring \
    --p8=/NFShield/nat-tcp-v4 \
    --p9=/NFShield/maglev \
    --p10=/NFShield/lpm \
    --p11=/NFShield/monitoring \
    --p12=/NFShield/acl-fw \
    --p13=/NFShield/dpi \
    --p14=/NFShield/lpm \
    --p15=/NFShield/monitoring \
    # > /GEM5_DRAMSim2/sgx_nic/results/stdout_test_none.out \
    # 2> /GEM5_DRAMSim2/sgx_nic/stderr/stderr_test_none.out
