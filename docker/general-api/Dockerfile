FROM python:3.9
ENV TZ=Asia/Tokyo 

RUN apt-get update &&\
    apt-get install -y gpg-agent wget software-properties-common &&\
    wget -qO - https://repositories.intel.com/graphics/intel-graphics.key | apt-key add - &&\
    apt-add-repository 'deb [arch=amd64] https://repositories.intel.com/graphics/ubuntu focal main' &&\
    apt-get update &&\
    apt-get install -y intel-opencl-icd intel-level-zero-gpu level-zero intel-media-va-driver-non-free libmfx1 &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN apt-get update &&\
    apt install -y curl ffmpeg i965-va-driver &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN apt-get update &&\
    apt install -y curl python3-pip  &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN pip3 install -U fastapi uvicorn[standard] aiohttp aiofiles python-multipart aiopath
WORKDIR /
CMD /bin/bash
