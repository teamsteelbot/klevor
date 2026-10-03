#!/usr/bin/env bash

# Script to create necessary directories for Docker volumes
mkdir -p ./volumes/alloy-data
mkdir -p ./volumes/prometheus-data
mkdir -p ./volumes/loki-data
mkdir -p ./volumes/tempo-data
mkdir -p ./volumes/grafana-data