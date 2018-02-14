#!/bin/bash
VERSION=0.1.9

# Build the docker image.
docker build --no-cache=true -t docker.psi.ch:5000/detector_api_server .

# Push it to our repo.
docker tag docker.psi.ch:5000/detector_api_server docker.psi.ch:5000/detector_api_server:$VERSION
docker push docker.psi.ch:5000/detector_api_server:$VERSION
docker push docker.psi.ch:5000/detector_api_server
