#! /bin/bash
# Clemens Bauer

# Set initial paths
cwd=$(pwd)


singularity exec murfi-sif_latest.sif servedicoms img/dcm/feedback/ tmp/murfi_input 1200

