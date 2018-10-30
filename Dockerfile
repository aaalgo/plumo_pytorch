from nvidia/cuda:8.0-cudnn5-devel-ubuntu14.04
RUN apt-get update && apt-get install -y git python-pip python-dev python-matplotlib gfortran libopenblas-dev liblapack-dev libsm6 libxext6
RUN pip install -U wheel
RUN pip install numpy pandas 
RUN pip install cython==0.23 nvidia-ml-py==7.352.0 
RUN pip install scipy==0.18.1 nose pyparsing==2.1.4 scikit-image==0.12.3
RUN pip install http://download.pytorch.org/whl/cu80/torch-0.1.11.post5-cp27-none-linux_x86_64.whl
RUN pip install dicom jinja2 
RUN pip install --upgrade pip
RUN pip install opencv-python
RUN mkdir /work/
ADD res/ /work/
WORKDIR /work
RUN git clone https://github.com/jcausey-astate/grt123-DSB2017.git grt123-DSB2017
#RUN git checkout d5ed68ecd5bd5bd4e8fcb7ffae89a490d6ce4a69
RUN bash patch/patch.sh
