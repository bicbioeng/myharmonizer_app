FROM jupyter/datascience-notebook:python-3.9.12

ARG GITHUB=6ad88af225c508d32214e94fbfabe8bec2e921a0

USER root

ENV PATH=/opt/conda/envs/myharmonizer/bin:/opt/conda/condabin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

WORKDIR /app

# install myharmonizer
RUN git clone https://$GITHUB@github.com/bicbioeng/myharmonizer.git

RUN apt-get update
RUN apt-get install -y wget

# update indices
RUN apt-get update -qq
# install two helper packages we need
RUN apt-get install -y --no-install-recommends software-properties-common dirmngr

RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
# add the R 4.0 repo from CRAN -- adjust 'focal' to 'groovy' or 'bionic' as needed
RUN add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"

RUN conda env create -f ./myharmonizer/myharmonizer/myharmonizer.yml python=3.9.12
RUN pip install ./myharmonizer/
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cp -a ./myharmonizer/myharmonizer/* .

#SHELL ["/bin/bash","-c"]
RUN apt-get install -y libssl-dev
RUN apt-get install -y libcurl4-openssl-dev
RUN Rscript -e "install.packages('BiocManager', repos='http://cran.us.r-project.org')"
RUN Rscript -e "BiocManager::install('RCurl')"
RUN Rscript -e "BiocManager::install('edgeR')"
RUN Rscript -e "BiocManager::install('DESeq2')"
RUN Rscript -e "install.packages('argparse',repos='http://cran.us.r-project.org')"
RUN Rscript -e "install.packages('plyr',repos='http://cran.us.r-project.org', dependencies = TRUE)"

COPY . .

CMD ["streamlit","run","app.py","--server.port",80]