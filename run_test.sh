#!/bin/bash
build/ARM/gem5.fast \
    --stats-file=test.txt \
    configs/dramsim2/dramsim2_se.py \
    --cpu-type=detailed \
    --caches \
    --l2cache \
    --maxinsts=1000000000 \
    --maxtick=2000000000000000 \
    --fixaddr \
    --rr_nc \
    --split_mshr \
    --split_rport \
    --dramsim2 \
    --tpturnlength=6 \
    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
    --systemcfg=./ext/DRAMSim2/system_tp.ini \
    --numpids=1 \
    --p0='/users/yangzhou/NF-GEM5/acl-fw'\
    # --fast-forward=1000000000 \
    # --outputfile=/dev/null \
    # > results/stdout_tp_detailed_astartl6_astartl6_c4MB.out
