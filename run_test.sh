#!/bin/bash
# build/ARM/gem5.fast configs/dramsim2/dramsim2_se.py \
#     --cpu-type=timing \
#     --caches \
#     --dramsim2 \
#     --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
#     --systemcfg=./ext/DRAMSim2/system_tp.ini \
#     --p0="/users/yangzhou/NF-GEM5/dpi" \


build/ARM/gem5.fast configs/dramsim2/dramsim2_se.py \
    --cpu-type=timing \
    --caches --l2cache \
    --dramsim2 \
    --devicecfg=./ext/DRAMSim2/ini/DDR3_micron_16M_8B_x8_sg15.ini \
    --systemcfg=./ext/DRAMSim2/system_tp.ini \
    --outputfile=./results/tp_astar_bzip2.out \
    --p0=/users/yangzhou/NF-GEM5/dpi \
    --p1=/users/yangzhou/NF-GEM5/dpi \
    -c /users/yangzhou/NF-GEM5/dpi
