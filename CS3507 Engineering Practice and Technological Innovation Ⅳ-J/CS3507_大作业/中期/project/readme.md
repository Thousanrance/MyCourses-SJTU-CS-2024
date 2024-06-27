## Readme

### 文件结构

```
.
├── data
│   ├── baseline.py
│   ├── emotion analysis based on text_refresh.csv
│   ├── emotion analysis based on text_top.csv
│   ├── Emotion Detection from Text_refresh.csv
│   ├── Emotion Detection from Text_top.csv
│   ├── Emotions in text_refresh.csv
│   ├── Emotions in text_top.csv
│   └── __pycache__
├── gpt2
│   ├── config.json
│   ├── generation_config.json
│   ├── merges.txt
│   ├── pytorch_model.bin
│   ├── tokenizer_config.json
│   ├── tokenizer.json
│   └── vocab.json
├── log
├── model
├── test.py
└── train.py
```

其中data存放csv数据，gpt2存放提前下载到本地的预处理模型，log存放各类日志记录，model存放微调完成的gpt2新模型。

### 数据预处理

data中没有保留原始数据集，只保存了经过refresh的统一格式数据集，如果你希望使用其他数据集，请手动根据本例的csv设计格式

从数据集中划分平衡的小量训练集，请使用baseline.py，具体参数在文件中手动修改

```bash
python data/baseline
```

### 训练

训练使用的数据集、输出模型名称，都在train.py中手动修改

```bash
python train.py
```

### 测试

测试使用的数据集、调用模型名称，都在test.py中手动修改

```bash
python test.py
```

### 日志

除tqdm提供的进度条，运行过程的全部log都以打印到屏幕的方式呈现，故如果需要记录请通过输出重定向的方式手动记录log

例如：

```bash
python train.py > log/log_eit.txt
```