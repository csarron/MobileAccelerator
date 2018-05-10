#!/usr/bin/env bash

declare -a models=("alexnet_v2" "squeezenet" "inception_v3"
                    "mobilenet_v1_1.0" "mobilenet_v2_1.0") #  "resnet_v1_50" is not working

for model in "${models[@]}"
do
    echo
    echo -e "\033[34m running \033[1mSNPE\033[0m for \033[1m\033[36m${model}\033[0m..."
    echo

    if [[ ${model} = "mobilenet"* ]]; then
        suffix="_224"
    else
        suffix=""
    fi
    frozen_graph=data/${model}${suffix}/${model}${suffix}.frozen.pb

    python snpe/run_snpe.py --model ${frozen_graph}

done

echo -e "\033[1mAll done"
