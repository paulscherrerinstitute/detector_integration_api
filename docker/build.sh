#!/bin/bash
VERSION=0.0.3
SLS_DETECTOR_VERSION=3.0

sh get_sls_detectors.sh ${SLS_DETECTOR_VERSION}

docker build --no-cache=true -t docker.psi.ch:5000/detector_api_server .
docker tag docker.psi.ch:5000/detector_api_server docker.psi.ch:5000/detector_api_server:$VERSION
docker push docker.psi.ch:5000/detector_api_server:$VERSION
docker push docker.psi.ch:5000/detector_api_server
