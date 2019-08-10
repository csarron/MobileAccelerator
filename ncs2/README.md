```
python common\export_inference_graph.py -m alexnet_fw1 -o alexnet_fw1.inf.pb
python common\gen_weights.py -m alexnet_fw1 -o alexnet_fw1.ckpt
python common\freeze_model.py -c alexnet_fw1.ckpt -g alexnet_fw1.inf.pb
python "C:\Program Files (x86)\IntelSWTools\openvino\deployment_tools\model_optimizer\mo_tf.py" --input_model alexnet_fw1.frozen.pb --output_dir C:/Users/alexa/Documents/NCS/ir --data_type FP16 --input_shape (1,224,224,3)
python "C:\Program Files (x86)\IntelSWTools\openvino_2019.1.148\deployment_tools\inference_engine\samples\python_samples\classification_sample\classification_sample.py" --model C:\Users\alexa\Documents\NCS\ir\alexnet_fw1.frozen.xml --input C:\Users\alexa\Documents\NCS\test_pictures\car.jpg --device MYRIAD --perf_counts --labels C:\Users\alexa\Documents\NCS\ir\squeezenet1.1.labels
```