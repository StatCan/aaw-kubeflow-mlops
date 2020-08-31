#!/usr/bin/env bash

set -e

while getopts "r:" option;
    do
    case "$option" in
        r ) REGISTRY_NAME=${OPTARG};;
    esac
done
IMAGE=${REGISTRY_NAME}.azurecr.io/iowa-register-kubeflow-artifacts
docker build -t $IMAGE . && docker push $IMAGE
