FROM conda/miniconda3-centos7

ENV RUN_DIR /runners
ENV TERM=xterm

# Create directory structure.
RUN mkdir -p ${RUN_DIR}

# Install detector integration API.
RUN conda install -c paulscherrerinstitute detector_integration_api --yes

# Install sls_detector_software
RUN conda install -c slsdetectorgroup sls_detector_software --yes

# Copy run files.
ADD startup.sh ${RUN_DIR}
RUN chmod +x ${RUN_DIR}/startup.sh

WORKDIR ${RUN_DIR}

CMD ${RUN_DIR}/startup.sh