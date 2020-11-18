FROM continuumio/miniconda3

WORKDIR /code/backend

RUN conda create --name project

RUN echo "source activate project" > ~/.bashrc

ENV PATH /opt/conda/envs/env/bin:$PATH

RUN conda install django

CMD [ "/bin/bash" ]