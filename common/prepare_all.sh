#!/usr/bin/env bash

python common/download_model.py -a

declare -a models=("alexnet_v2" "squeezenet" "mobilenet_v1_1.0" "mobilenet_v2_1.0"
                   "inception_v3") #  "resnet_v1_50" needs to be handled differently

for model in "${models[@]}"
do
    echo
    echo -e "\033[1m\033[34mpreparing \033[36m${model}...\033[0m"
    echo

    if [[ ${model} = "mobilenet"* ]]; then
        suffix="_224"
    else
        suffix=""
    fi

    checkpoint=data/${model}${suffix}/${model}${suffix}.ckpt
    inf_graph=data/${model}${suffix}/${model}${suffix}.inf.pb
    frozen_graph=data/${model}${suffix}/${model}${suffix}.frozen.pb

    python common/slim/export_inference_graph.py -m ${model} -o ${inf_graph}
    python common/visualize_model.py ${inf_graph}

    python common/freeze_model.py -c ${checkpoint} -g ${inf_graph}

    python ncs/convert_model.py -c ${checkpoint} -g ${inf_graph}
    python tflite/convert_model.py ${frozen_graph}


done

echo -e "\033[1mAll done"
