#!/bin/bash

cd ${RUN_DIR}

# Check if the SLS detector config file is present.
if [ ! -f /etc/eiger_9m_10gb.config ]
then
    echo "File /etc/eiger_9m_10gb.config not found in container.";
    exit -1;
fi

# Check if the needed environment variables are present.
if [ -z "${DIA_REST_ADDRESS}" ]; then echo "ENV variable DIA_REST_ADDRESS is not set."; exit -1; fi
if [ -z "${DIA_REST_PORT}" ]; then echo "ENV variable DIA_REST_PORT is not set."; exit -1; fi
if [ -z "${DIA_LOG_LEVEL}" ]; then echo "ENV variable DIA_LOG_LEVEL is not set."; exit -1; fi
if [ -z "${DIA_BACKEND_URL}" ]; then echo "ENV variable DIA_BACKEND_URL is not set."; exit -1; fi
if [ -z "${DIA_WRITER_URL}" ]; then echo "ENV variable DIA_WRITER_URL is not set."; exit -1; fi
if [ -z "${DIA_WRITER_INSTANCE_NAME}" ]; then echo "ENV variable DIA_WRITER_INSTANCE_NAME is not set."; exit -1; fi

# Configure the SLS detectors.
echo "Configure SLS detector..."
sls_detector_put 0-config /etc/detector.config
echo "Done."

# Run the API server.
echo "Run detector api server..."
detector_api_server -i ${DIA_REST_ADDRESS} -p ${DIA_REST_PORT} --log_level=${DIA_LOG_LEVEL} -b ${DIA_BACKEND_URL} -w ${DIA_WRITER_URL} --writer_instance_name=${DIA_WRITER_INSTANCE_NAME}
echo "Done."