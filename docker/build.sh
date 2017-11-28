#!/bin/bash
VERSION=0.1.8
SLS_DETECTOR_VERSION=3.0.1
GIT_USER=git

# Clone the sls_detector_software
git clone ${GIT_USER}@git.psi.ch:sls_detectors_software/sls_detectors_package.git sls_detectors_package
cd sls_detectors_package
sh checkout.sh $GIT_USER
sh gitall.sh checkout $SLS_DETECTOR_VERSION
cd -

# Build the docker image.
docker build --no-cache=true -t docker.psi.ch:5000/detector_api_server .

# Push it to our repo.
docker tag docker.psi.ch:5000/detector_api_server docker.psi.ch:5000/detector_api_server:$VERSION
docker push docker.psi.ch:5000/detector_api_server:$VERSION
docker push docker.psi.ch:5000/detector_api_server
