#!/bin/bash

cd ${RUN_DIR}

# Run detector receivers.
python dia_run_receivers.py ${DIA_RECEIVERS_INIT_PORT} ${DIA_RECEIVERS_NUMBER} &

# Run the API server.
detector_api_server -i ${DIA_REST_ADDRESS} -p ${DIA_REST_PORT} --log_level=${DIA_LOG_LEVEL} -b ${DIA_BACKEND_URL} -w ${DIA_WRITER_URL} --writer_instance_name=${DIA_WRITER_INSTANCE_NAME}
