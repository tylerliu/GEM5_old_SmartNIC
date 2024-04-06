
FROM ubuntu:18.04

RUN apt update -y
RUN apt-get install -y git vim build-essential gcc-arm-linux-gnueabi g++-arm-linux-gnueabi scons swig m4 libgoogle-perftools-dev zlib1g zlib1g-dev python-dev git-lfs

RUN apt install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt install -y python3.7

RUN git clone https://github.com/tylerliu/GEM5_old_SmartNIC gem5

WORKDIR gem5
RUN scons build/ARM/gem5.opt -j 2

WORKDIR /
RUN git clone https://github.com/YangZhou1997/NFShield

WORKDIR /NFShield
RUN sed -i 's:/users/yangzhou/:/:g' *.c
RUN make
RUN git lfs pull -I data/

WORKDIR /gem5

CMD ["sleep", "infinity"]
