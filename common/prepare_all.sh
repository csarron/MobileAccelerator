#!/usr/bin/env bash

python common/download_model.py -a

declare -a models=("inception_v3" "mobilenet_v1_1.0" "mobilenet_v2_1.0"
                "mobilenet_v2_1.3" "mobilenet_v2_1.4") #  "resnet_v1_50" needs to be handled differently

for model in "${models[@]}"
do
    echo
    echo -e "\033[1m\033[34mpreparing \033[36m${model}...\033[0m"
    echo
    python common/slim/export_inference_graph.py -m ${model} -o data/${model}/${model}_inf.pb
    python common/visualize_model.py data/${model}/${model}_inf.pb

    if [[ ${model} = "mobilenet"* ]]; then
        suffix="_224"
    else
        suffix=""
    fi
    python common/freeze_model.py -c data/${model}/${model}${suffix}.ckpt -g data/${model}/${model}_inf.pb
    python ncs/convert_model.py -c data/${model}/${model}${suffix}.ckpt -g data/${model}/${model}_inf.pb

    #python ncs/run_ncs.py -m data/mobilenet_v2_1.4/ncs_mobilenet_v2_1.4_224.meta -p ~/p3dl/bin/python
done

echo -e "\033[1mAll done"
