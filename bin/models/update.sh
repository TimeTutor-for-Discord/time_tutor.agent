#!/bin/bash

SCHEMA_PATH="./schema/json"
MODEL_PATH="./models"
CODE_GEN="./venv/bin/datamodel-codegen"

# validation
if [ ! -d ${SCHEMA_PATH} ]; then 
    echo "${SCHEMA_PATH} does not exists. "
    echo "You need to check if the submodule has been checked out correctly because the directory is missing."
    exit 1
fi
if [ ! -d ${MODEL_PATH} ]; then mkdir ./models; fi

for tgt in $(find "${SCHEMA_PATH}" -type f); do
    tgt_filename=$(basename ${tgt})
    ${CODE_GEN} --input-file-type json --input ${tgt} --output "${MODEL_PATH}/${tgt_filename%.*}.py"
done
