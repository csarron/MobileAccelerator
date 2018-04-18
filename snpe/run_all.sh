#!/usr/bin/env bash

declare -a models=("inception_v3" "mobilenet_v1_1.0" "mobilenet_v2_1.0"
                "mobilenet_v2_1.3" "mobilenet_v2_1.4") #  "resnet_v1_50" needs to be handled differently

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

    python snpe/run_snpe.py --model data/${model}/${model}${suffix}.frozen.pb

done

echo -e "\033[1mAll done"
