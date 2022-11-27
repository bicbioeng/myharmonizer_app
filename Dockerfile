FROM python:3.9

ARG GITHUB=6ad88af225c508d32214e94fbfabe8bec2e921a0

WORKDIR /app

# install myharmonizer
RUN git clone https://$GITHUB@github.com/bicbioeng/myharmonizer.git
RUN pip install ./myharmonizer/

RUN apt-get update
RUN apt-get install -y wget

# update indices
RUN apt-get update -qq
# install two helper packages we need
RUN apt-get install -y --no-install-recommends software-properties-common dirmngr
# add the signing key (by Michael Rutter) for these repos
# To verify key, run gpg --show-keys /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
# Fingerprint: E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
# add the R 4.0 repo from CRAN -- adjust 'focal' to 'groovy' or 'bionic' as needed
RUN add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"

RUN conda env create -f ./myharmonizer/myharmonizer.yml python=3.9.12

#SHELL ["/bin/bash","-c"]

#RUN apt-get install -y libssl-dev

#RUN apt-get install -y libcurl4-openssl-dev

#RUN Rscript -e "install.packages('BiocManager', repos='http://cran.us.r-project.org')"
#RUN Rscript -e "BiocManager::install('RCurl')"
#RUN Rscript -e "BiocManager::install('edgeR')"
#RUN Rscript -e "BiocManager::install('DESeq2')"
#RUN Rscript -e "install.packages('argparse',repos='http://cran.us.r-project.org')"
#RUN Rscript -e "install.packages('plyr',repos='http://cran.us.r-project.org', dependencies = TRUE)"

COPY . .
