FROM conda/miniconda3-centos7

ENV INSTALL_DIR /install
ENV RUN_DIR /runners
ENV TERM=xterm

# Install needed libraries.
RUN yum install git make gcc-c++ -y

# Create directory structure.
RUN mkdir -p ${INSTALL_DIR}
RUN mkdir -p ${RUN_DIR}

# Install the SLS detector software
ADD sls_detectors_package/ ${INSTALL_DIR}/
RUN cd ${INSTALL_DIR}; make REST=no textclient receiver
ENV PATH="${INSTALL_DIR}/bin:${PATH}"

# Install detector integration API.
RUN conda install -c paulscherrerinstitute detector_integration_api --yes

# Copy run files.
ADD startup.sh ${RUN_DIR}
RUN chmod +x ${RUN_DIR}/startup.sh
ADD run_receivers.py ${RUN_DIR}

WORKDIR ${RUN_DIR}

ENTRYPOINT ["${RUN_DIR}/startup.sh"]