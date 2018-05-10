#!/usr/bin/env bash

declare -a models=("alexnet_v2" "squeezenet" "inception_v3"
                    "mobilenet_v1_1.0" "mobilenet_v2_1.0" "resnet_v1_50")

for model in "${models[@]}"
do
    echo
    echo -e "\033[1m\033[34m running \033[36m${model}\033[0m on \033[1mNCS\033[0m..."
    echo

    if [[ ${model} = "mobilenet"* ]]; then
        suffix="_224"
    else
        suffix=""
    fi

    ncs_graph=data/${model}${suffix}/ncs_${model}${suffix}.meta
    python ncs/run_ncs.py -m ${ncs_graph} -p ~/p3dl/bin/python

done

echo -e "\033[1mAll done"
