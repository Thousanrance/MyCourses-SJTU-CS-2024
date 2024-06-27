## Readme

### 文件结构

```
.
├── bert
├── chinese
│   ├── bert_zh_emotion_classification_2.ipynb
│   ├── bert_zh_emotion_classification_7(5epoch).ipynb
│   ├── bert_zh_emotion_classification_7.ipynb
│   ├── ChnSentiCorp_refresh.csv
│   └── OCEMOTION_refresh.csv
├── data
│   ├── gnrt
│     ├── clear.py
│     └── shfl.py
│   ├── baseline.py
│   ├── dvd.py
│   ├── emotion analysis based on text_refresh.csv
│   ├── Emotion Detection from Text_refresh.csv
│   ├── Emotions in text_refresh.csv
│   ├── love_letters_dataset.txt
│   ├── shfl.py
│   ├── Short Jokes Dataset_refresh.txt
│   ├── Stress Detection from Social Media Articles_refresh.txt
│   └── tosix.py
├── gpt2
├── log
├── model
│   └── bert_6f3_2
├── baseline.py
├── test.py
├── test_bert.py
├── test_gnrt.py
├── test_token.py
├── test.py
├── train.py
├── train_bert.py
├── train_gnrt.py
└── train_token.py
```

其中data存放csv数据，gpt2/bert存放提前下载到本地的预处理模型，log存放各类日志记录，model存放微调完成的gpt2新模型，chinese存放中文相关数据集与工程。

### 数据预处理

data中没有保留原始数据集，只保存了经过refresh的统一格式数据集，如果你希望使用其他数据集，请手动根据本例的csv设计格式

从数据集中划分平衡的小量训练集，请使用baseline.py，具体参数在文件中手动修改

```bash
python data/baseline.py
```

从数据集中划分训练测试集，请使用dvd.py，具体参数在文件中手动修改

```bash
python data/dvd.py
```

洗混数据集，请使用shfl.py，具体参数在文件中手动修改

```bash
python data/shfl.py
```

从13类数据集中提取6类数据集，请使用tosix.py，具体参数在文件中手动修改

```bash
python data/tosix.py
```

处理生成模型，请使用gnrt目录下的shfl.py与clear.py，具体参数在文件中手动修改

### 训练

训练使用的数据集、输出模型名称，都在train.py中手动修改

```bash
python train.py
```

在主目录下的train，分别是：

* `train.py` gpt2上分类模型训练
* `train_bert.py` bert上分类模型训练
* `train_gnrt.py` gpt2上生成模型训练
* `train_token.py` bert上修改token后分类模型训练

### 测试

测试使用的数据集、调用模型名称，都在test.py中手动修改

```bash
python test.py
```

在主目录下的test，分别是：

* `test.py` gpt2上分类模型测试
* `test_bert.py` bert上分类模型测试
* `test_gnrt.py` gpt2上生成模型测试
* `test_token.py` bert上修改token后分类模型测试

### 关于中文模型

中文数据的相关作业与英文模型间相对独立，故单独连同数据与工程存放在单独的目录下，可以根据ipynb的说明依序进行测试

### 日志

除tqdm提供的进度条，运行过程的全部log都以打印到屏幕的方式呈现，故如果需要记录请通过输出重定向的方式手动记录log

这种方法主要应用于第一部分，在第二部分中bert直接采用报告式生成

例如：

```bash
python train.py > log/log_eit.txt
```