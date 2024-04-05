#!/bin/bash
gdb --args build/ARM/gem5.debug \
    --remote-gdb-port=0 \
    --outdir=/gem5/sgx_nic/m5out/test_tp \
    --stats-file=test_tp_stats.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed --clock=2.4GHz \
    --cacheline_size=128 \
    --caches --l2cache \
    --l2config=setpartition \
    --l2_size=256kB --l2_assoc=16 \
    --fixaddr \
    --rr_nc \
    --split_mshr \
    --split_rport \
    --dramsim2 \
    --tpturnlength=6 \
    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
    --systemcfg=./ext/DRAMSim2/system_tp.ini \
    --outputfile=/dev/null \
    --fast-forward=2000000 \
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
    # > /gem5/sgx_nic/results/stdout_test_tp.out \
    # 2> /gem5/sgx_nic/stderr/stderr_test_tp.out
