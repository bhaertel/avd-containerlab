#!/usr/bin/env bash

set -euo pipefail

state_dir="${HOME}/.cache/arista-devcontainer"
state_file="${state_dir}/eos-import-${ARISTA_GET_EOS_VERSION:-unset}.done"

mkdir -p "${state_dir}"

if [[ -z "${ARISTA_GET_EOS_VERSION:-}" ]]; then
    echo "Skipping EOS import: ARISTA_GET_EOS_VERSION is not set."
    exit 0
fi

if [[ -f "${state_file}" ]]; then
    echo "EOS ${ARISTA_GET_EOS_VERSION} already imported for this container."
    exit 0
fi

ardl get eos --version "${ARISTA_GET_EOS_VERSION}" --import-docker --format cEOS
touch "${state_file}"