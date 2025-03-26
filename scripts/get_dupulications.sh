#! /bin/bash

SONARQUBE_URL="http://XXX:9000"
SONAR_PROJECT_KEY="XXX"
USER="admin"
PW="XXX"
OUTPUT_FILE="duplication_report.csv"

curl -u ${USER}:${PW} "${SONARQUBE_URL}/api/measures/component_tree?component=${YOUR_PROJECT_KEY}&metricKeys=duplicated_lines_density" |
  jq -r '.components[] | [.key, .measures[0].value] | @csv' \
    >${OUTPUT_FILE}
