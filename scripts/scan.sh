#! /bin/bash

SONARQUBE_URL="XXX:9000"
YOUR_PROJECT_KEY="test"
SRC_DIR="/XXX"
TOKEN="XXX"

docker run \
    --rm \
    -e SONAR_HOST_URL="http://${SONARQUBE_URL}" \
    -e SONAR_SCANNER_OPTS="-Dsonar.projectKey=${YOUR_PROJECT_KEY}" \
    -e SONAR_TOKEN=${TOKEN} \
    -v "${SRC_DIR}:/usr/src" \
    sonarsource/sonar-scanner-cli

# -e SONAR_SCANNER_OPTS="-Dsonar.java.binaries=bin" \
