#!/usr/bin/env bash

# Start at the repo root
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd ..

# Activate virtual environment
source source_to_activate.sh

# Go to the model merging directory
cd model_merging

# Install dependencies
pip install absl-py tensorflow tensorflow_datasets tensorflow_probability


#######################
# Run the isometric model merging as shown in ./model_merging/README.md

EVAL_TASK=rte
RTE_MODEL=textattack/roberta-base-RTE
MNLI_MODEL=textattack/roberta-base-MNLI


# Isometric merge.
PYTHONPATH=. python3 ./scripts/merge_and_evaluate.py  \
    --models=$RTE_MODEL,$MNLI_MODEL \
    --glue_task=$EVAL_TASK
