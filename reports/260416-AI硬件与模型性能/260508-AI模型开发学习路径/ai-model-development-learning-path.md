# AI 模型开发学习路线：从 Python 到 PyTorch、LLM、Triton

生成日期：2026-05-08  
适用对象：已经具备 Python 基础，想系统学习 AI 模型开发的人  
总体目标：从“会调用模型”逐步进阶到“能训练模型、理解模型、微调模型、部署模型，并具备进一步学习推理优化/Triton 的基础”。

---

## 0. 总体路线图

建议按下面顺序学习：

```text
阶段 1：机器学习基础
阶段 2：NumPy/Pandas/数据处理能力
阶段 3：scikit-learn 建模流程
阶段 4：PyTorch 深度学习基础
阶段 5：从零写训练循环
阶段 6：Transformer 与大模型基础
阶段 7：Hugging Face 与模型微调
阶段 8：RAG 与 LLM 应用开发
阶段 9：模型部署与推理服务
阶段 10：性能优化、CUDA 基础、Triton
```

建议节奏：每天 1.5 到 3 小时，整体 4 到 6 个月。  
如果每天能投入 4 小时以上，可以压缩到 2.5 到 3 个月。

---

## 1. 学习环境准备

### 1.1 目标

你需要先准备一个稳定的 Python AI 开发环境，后续所有任务都在这个环境中完成。

### 1.2 要安装的工具

1. Python 3.10 或 3.11
2. Git
3. VS Code 或 Cursor
4. Conda、Miniconda 或 uv，三选一
5. JupyterLab 或 VS Code Notebook

### 1.3 推荐目录结构

```text
ai-learning/
  00-notes/
  01-ml-basics/
  02-sklearn-projects/
  03-pytorch-basics/
  04-deep-learning-projects/
  05-transformer-llm/
  06-rag-apps/
  07-deployment/
  08-triton-optimization/
```

### 1.4 创建环境

如果使用 conda：

```bash
conda create -n ai-dev python=3.11 -y
conda activate ai-dev
pip install numpy pandas matplotlib scikit-learn jupyterlab torch torchvision torchaudio transformers datasets accelerate
```

如果使用 uv：

```bash
uv venv
source .venv/bin/activate
uv pip install numpy pandas matplotlib scikit-learn jupyterlab torch torchvision torchaudio transformers datasets accelerate
```

### 1.5 验收标准

你需要能成功运行下面代码：

```python
import numpy as np
import pandas as pd
import sklearn
import torch
import transformers

print(np.__version__)
print(pd.__version__)
print(sklearn.__version__)
print(torch.__version__)
print(transformers.__version__)
print(torch.cuda.is_available())
```

---

## 2. 阶段 1：机器学习核心概念

### 2.1 学习目标

这一阶段不是为了背公式，而是建立“模型训练到底在做什么”的直觉。

完成后你应该能解释：

1. 什么是特征 feature
2. 什么是标签 label
3. 什么是训练集、验证集、测试集
4. 什么是损失函数
5. 什么是梯度下降
6. 什么是过拟合和欠拟合
7. 准确率、召回率、精确率、F1 分数分别是什么意思

### 2.2 学习顺序

#### Step 1：理解监督学习

要点：

- 输入：特征 X
- 输出：标签 y
- 目标：学习一个函数 f，让 f(X) 尽量接近 y

练习：

- 找 3 个生活中的监督学习例子
- 对每个例子写出 feature 和 label

示例：

```text
任务：预测房价
feature：面积、楼层、城市、地铁距离、房龄
label：房价
```

#### Step 2：理解训练集和测试集

要点：

- 训练集用于让模型学习
- 测试集用于评估模型没见过的数据
- 不能用测试集参与训练

练习：

- 用自己的话解释为什么不能只看训练集准确率

#### Step 3：理解损失函数

要点：

- 损失函数衡量预测值和真实值之间的差距
- 回归常用 MSE
- 分类常用 Cross Entropy

练习：

- 手算 3 个预测值和真实值的 MSE

#### Step 4：理解梯度下降

要点：

- 模型参数一开始是随机或初始化出来的
- 损失函数告诉我们模型错得有多离谱
- 梯度告诉我们参数应该往哪个方向调整
- 学习率决定每次调整多大

练习：

- 画一条 U 形曲线，标出当前位置、梯度方向、下一步位置

#### Step 5：理解过拟合

要点：

- 训练集表现很好，测试集表现差，通常是过拟合
- 模型记住了训练数据，而不是学到通用规律

练习：

- 写出 3 种缓解过拟合的方法：更多数据、正则化、降低模型复杂度、早停、数据增强等

### 2.3 阶段验收

你应该能不用查资料回答：

1. 为什么要拆训练集和测试集？
2. 损失函数和准确率有什么区别？
3. 学习率太大会怎样？太小会怎样？
4. 什么是过拟合？如何发现？

---

## 3. 阶段 2：NumPy、Pandas、Matplotlib

### 3.1 学习目标

AI 模型开发离不开数据处理。这个阶段的目标是让你能熟练读取、清洗、分析和可视化数据。

### 3.2 NumPy 学习步骤

#### Step 1：数组创建

需要掌握：

```python
np.array
np.zeros
np.ones
np.arange
np.linspace
np.random.randn
```

练习：

- 创建一个 100 行 4 列的随机矩阵
- 计算每一列的均值和标准差

#### Step 2：数组索引和切片

需要掌握：

```python
x[0]
x[:, 0]
x[0:10]
x[x > 0]
```

练习：

- 从随机矩阵中筛选出第一列大于 0 的所有行

#### Step 3：矩阵运算

需要掌握：

```python
a + b
a * b
a @ b
np.dot(a, b)
np.mean
np.std
np.sum
```

练习：

- 手写一个线性模型：`y = X @ w + b`

### 3.3 Pandas 学习步骤

#### Step 1：读取数据

需要掌握：

```python
pd.read_csv
df.head()
df.info()
df.describe()
```

练习：

- 下载 Titanic 数据集
- 输出数据形状、字段名、缺失值数量

#### Step 2：选择和过滤数据

需要掌握：

```python
df["col"]
df[["col1", "col2"]]
df[df["age"] > 18]
df.loc[]
df.iloc[]
```

练习：

- 找出所有年龄大于 18 岁且幸存的人

#### Step 3：缺失值处理

需要掌握：

```python
df.isna().sum()
df.dropna()
df.fillna()
```

练习：

- 对 Titanic 的 Age 字段用中位数填充

#### Step 4：简单可视化

需要掌握：

```python
import matplotlib.pyplot as plt
df["age"].hist()
plt.scatter(x, y)
plt.plot(x, y)
```

练习：

- 画出年龄分布图
- 画出不同性别的生存率柱状图

### 3.4 阶段项目

项目：Titanic 数据探索报告

你需要输出一个 notebook，包含：

1. 数据加载
2. 字段解释
3. 缺失值统计
4. 年龄分布图
5. 性别与生存率关系
6. 舱位等级与生存率关系
7. 你自己的 3 条观察结论

---

## 4. 阶段 3：scikit-learn 建模流程

### 4.1 学习目标

学会标准机器学习建模流程：加载数据、划分数据、训练模型、评估模型、保存模型。

### 4.2 标准流程

你要反复练习下面流程：

```text
加载数据
→ 选择特征和标签
→ 划分训练集/测试集
→ 创建模型
→ fit 训练
→ predict 预测
→ metrics 评估
→ 分析错误样本
```

### 4.3 第一个模型：鸢尾花分类

步骤：

1. 使用 `load_iris()` 加载数据
2. 查看 `data`、`target`、`feature_names`、`target_names`
3. 使用 `train_test_split` 切分数据
4. 创建 `LogisticRegression`
5. 调用 `model.fit(X_train, y_train)`
6. 调用 `model.predict(X_test)`
7. 使用 `accuracy_score` 计算准确率
8. 打印 5 个预测结果和真实标签

验收标准：

- 能输出测试集准确率
- 能解释每一行代码在做什么
- 能说清楚模型输入和输出分别是什么

### 4.4 第二个模型：房价回归

步骤：

1. 准备一个房价数据集
2. 选择面积、房间数、地段等字段作为特征
3. 选择价格作为标签
4. 使用 `LinearRegression`
5. 使用 MSE、MAE、R2 评估
6. 画预测值和真实值散点图

验收标准：

- 能解释回归和分类的区别
- 能解释 MAE 和 MSE 的区别

### 4.5 第三个模型：Titanic 生存预测

步骤：

1. 读取 Titanic 数据
2. 处理缺失值
3. 把性别、舱位等类别字段转为数字
4. 训练 Logistic Regression、RandomForest 两个模型
5. 比较两个模型准确率
6. 输出 confusion matrix

验收标准：

- 能完成基础特征工程
- 能比较不同模型效果
- 能解释混淆矩阵

---

## 5. 阶段 4：PyTorch 基础

### 5.1 学习目标

从 scikit-learn 的“调用模型”进入 PyTorch 的“自己定义模型和训练过程”。

### 5.2 Tensor 基础

步骤：

1. 创建 tensor
2. 查看 shape、dtype、device
3. 做加减乘除
4. 做矩阵乘法
5. 在 CPU 和 GPU 之间移动 tensor

必须掌握：

```python
torch.tensor
torch.randn
x.shape
x.dtype
x.device
x.to("cuda")
x.cpu()
x @ w
```

练习：

- 用 torch 实现 `y = X @ w + b`

### 5.3 autograd 自动求导

步骤：

1. 创建带 `requires_grad=True` 的 tensor
2. 计算 loss
3. 调用 `loss.backward()`
4. 查看 `.grad`
5. 理解梯度累积，学会 `zero_grad()`

练习：

- 对函数 `y = x ** 2 + 3x + 1` 求导

### 5.4 nn.Module

步骤：

1. 定义一个继承 `nn.Module` 的类
2. 在 `__init__` 中定义层
3. 在 `forward` 中定义前向传播
4. 创建模型实例
5. 输入 tensor 得到输出

必须掌握：

```python
class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.linear = nn.Linear(4, 3)

    def forward(self, x):
        return self.linear(x)
```

### 5.5 Dataset 和 DataLoader

步骤：

1. 理解 Dataset 表示数据集
2. 理解 DataLoader 负责 batch、shuffle、并行加载
3. 使用 TensorDataset
4. 自定义 Dataset

练习：

- 把 iris 数据包装成 TensorDataset
- 用 DataLoader 每次取 16 条数据

### 5.6 训练循环

你必须能默写这个结构：

```python
for epoch in range(num_epochs):
    model.train()
    for x_batch, y_batch in train_loader:
        optimizer.zero_grad()
        logits = model(x_batch)
        loss = criterion(logits, y_batch)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        # validation
        pass
```

验收标准：

- 能解释每一行为什么存在
- 知道 `model.train()` 和 `model.eval()` 的区别
- 知道为什么验证时要用 `torch.no_grad()`

---

## 6. 阶段 5：深度学习项目

### 6.1 项目 1：MNIST 手写数字识别

步骤：

1. 使用 torchvision 下载 MNIST
2. 使用 transforms 把图片转 tensor
3. 创建 DataLoader
4. 定义 MLP 模型
5. 使用 CrossEntropyLoss
6. 使用 Adam 优化器
7. 训练 5 到 10 个 epoch
8. 输出测试集准确率
9. 随机展示 10 张图片和预测结果

验收标准：

- 测试准确率达到 95% 以上
- 能解释输入 shape 和输出 shape

### 6.2 项目 2：CIFAR-10 图像分类

步骤：

1. 加载 CIFAR-10
2. 定义简单 CNN
3. 训练模型
4. 比较 MLP 和 CNN 的效果
5. 分析错误分类样本

验收标准：

- 能解释卷积层、池化层、全连接层
- 能说出 CNN 为什么比 MLP 更适合图像

### 6.3 项目 3：文本分类

步骤：

1. 准备一个简单文本分类数据集
2. 分词
3. 构建词表
4. 把文本转成 token id
5. 使用 Embedding 层
6. 使用平均池化或 RNN 做分类
7. 输出准确率

验收标准：

- 能解释 token、vocab、embedding
- 能解释文本为什么不能直接输入神经网络

---

## 7. 阶段 6：Transformer 与大模型基础

### 7.1 学习目标

理解现代大模型的核心结构，而不是只会调用 API。

### 7.2 学习顺序

#### Step 1：Tokenizer

要点：

- 文本先被切成 token
- token 再被映射成 token id
- 模型处理的是数字，不是原始文字

练习：

- 用 Hugging Face tokenizer 对一句中文和一句英文分词
- 打印 token、token id、decode 后的结果

#### Step 2：Embedding

要点：

- Embedding 是 token id 到向量的映射
- 语义相近的 token 可能有相近向量

练习：

- 用 `nn.Embedding` 创建一个小词表
- 输入 token id，查看输出 shape

#### Step 3：Attention

要点：

- Attention 让每个 token 关注其他 token
- Q、K、V 是 attention 的核心
- Self-Attention 是 Transformer 的关键

练习：

- 手写一个简化版 scaled dot-product attention

#### Step 4：Multi-head Attention

要点：

- 多个 head 可以从不同角度学习关系
- 多头输出会 concat 再投影

练习：

- 画出 Multi-head Attention 的数据流

#### Step 5：Transformer Block

要点：

- Attention
- Feed Forward Network
- Residual Connection
- LayerNorm

练习：

- 用 PyTorch 写一个简化 Transformer Block

### 7.3 验收标准

你应该能解释：

1. Tokenizer 的作用
2. Embedding 的作用
3. Attention 为什么有 Q、K、V
4. Transformer block 由哪些部分组成
5. GPT 和 BERT 的基本区别

---

## 8. 阶段 7：Hugging Face 与模型微调

### 8.1 学习目标

学会使用预训练模型，并能在自己的数据上做简单微调。

### 8.2 学习步骤

#### Step 1：使用 pipeline

练习：

```python
from transformers import pipeline

classifier = pipeline("sentiment-analysis")
print(classifier("I love this movie!"))
```

目标：先体验模型调用流程。

#### Step 2：手动使用 tokenizer 和 model

步骤：

1. 加载 tokenizer
2. 加载 model
3. 对文本编码
4. 调用模型
5. 解析 logits

目标：理解 pipeline 背后做了什么。

#### Step 3：使用 datasets

步骤：

1. 加载公开数据集
2. 查看字段
3. 写 tokenize 函数
4. 使用 map 处理数据

#### Step 4：使用 Trainer 微调

步骤：

1. 加载预训练模型
2. 准备训练集和验证集
3. 设置 TrainingArguments
4. 创建 Trainer
5. 调用 train
6. 调用 evaluate

验收标准：

- 能微调一个文本分类模型
- 能保存模型
- 能加载自己保存的模型做预测

### 8.3 LoRA/PEFT 入门

学习顺序：

1. 先理解全量微调为什么贵
2. 理解 LoRA 是低秩适配
3. 使用 PEFT 对小模型做 LoRA 微调
4. 比较训练参数量

验收标准：

- 能解释 LoRA 不是重新训练整个模型
- 能说出 LoRA 的优点和局限

---

## 9. 阶段 8：RAG 与 LLM 应用开发

### 9.1 学习目标

做出一个能读取本地文档并回答问题的 AI 应用。

### 9.2 RAG 核心流程

```text
文档
→ 切分 chunk
→ embedding
→ 存入向量数据库
→ 用户提问
→ 问题 embedding
→ 检索相关 chunk
→ 拼接 prompt
→ LLM 生成答案
```

### 9.3 学习步骤

#### Step 1：理解 embedding

练习：

- 对 5 句话计算 embedding
- 计算句子之间的 cosine similarity

#### Step 2：文档切分

练习：

- 把一篇 Markdown 文档按段落切分
- 控制每个 chunk 的长度

#### Step 3：向量检索

练习：

- 使用 FAISS 或 Chroma 存储向量
- 输入问题，返回最相关的 3 个 chunk

#### Step 4：组装 Prompt

练习：

- 把检索到的 chunk 放入 prompt
- 要求模型只能基于上下文回答

#### Step 5：做成小应用

练习：

- 用 FastAPI 或 Streamlit 做一个界面
- 上传文档
- 提问
- 返回答案和引用来源

验收标准：

- 能完成端到端本地文档问答
- 答案能显示引用来源
- 能解释 RAG 和微调的区别

---

## 10. 阶段 9：模型部署与推理服务

### 10.1 学习目标

把模型从 notebook 变成可被其他程序调用的服务。

### 10.2 学习步骤

#### Step 1：保存和加载模型

需要掌握：

```python
torch.save
torch.load
model.state_dict()
model.load_state_dict()
```

#### Step 2：FastAPI 封装推理接口

步骤：

1. 创建 `/predict` 接口
2. 接收 JSON 输入
3. 预处理输入
4. 调用模型
5. 返回预测结果

#### Step 3：Docker 化

步骤：

1. 写 Dockerfile
2. 安装依赖
3. 暴露端口
4. 启动 FastAPI

#### Step 4：本地模型服务

学习：

- Ollama
- llama.cpp
- vLLM

验收标准：

- 能通过 HTTP 调用模型
- 能解释 batch、latency、throughput
- 能知道什么时候用 vLLM，而不是普通 transformers generate

---

## 11. 阶段 10：性能优化、CUDA 基础、Triton

### 11.1 学习目标

如果你的目标是 AI Infra、LLM 推理加速、底层性能优化，这一阶段非常重要。  
如果你的目标只是 AI 应用开发，可以晚点学。

### 11.2 学习顺序

```text
PyTorch 性能分析
→ GPU 基础
→ CUDA 编程概念
→ 常见算子瓶颈
→ Triton 基础 kernel
→ matmul/softmax/LayerNorm/attention 优化
```

### 11.3 PyTorch 性能分析

学习：

1. `torch.profiler`
2. GPU 利用率
3. 显存占用
4. batch size 对吞吐的影响
5. 数据加载瓶颈

练习：

- 对 MNIST 或 CIFAR-10 训练脚本做 profiler
- 找出最耗时的步骤

### 11.4 CUDA 基础概念

不要求一开始能写复杂 CUDA，但需要理解：

1. thread
2. block
3. grid
4. global memory
5. shared memory
6. memory coalescing
7. warp

练习：

- 画出 grid、block、thread 的关系图

### 11.5 Triton 学习步骤

#### Step 1：Vector Add

目标：写第一个 Triton kernel。

你要理解：

- `@triton.jit`
- program id
- block size
- mask
- load/store

#### Step 2：矩阵乘法 Matmul

目标：理解 LLM 中最核心的计算为什么是 GEMM。

你要理解：

- tile/block matmul
- SRAM/shared memory 思路
- 为什么不能一次性读完整矩阵

#### Step 3：Fused Softmax

目标：理解算子融合为什么能减少显存读写。

你要理解：

- softmax 的数值稳定性
- max trick
- 读写显存次数

#### Step 4：LayerNorm

目标：理解 Transformer 常见算子的优化。

#### Step 5：Attention

目标：理解 FlashAttention 类优化背后的思想。

### 11.6 验收标准

你应该能回答：

1. Triton 和 PyTorch 的关系是什么？
2. Triton 和 CUDA 的区别是什么？
3. 为什么算子融合能提升性能？
4. matmul 为什么是 LLM 推理核心瓶颈？
5. 什么情况下应该自己写 Triton kernel？

---

## 12. 第一个学习任务：Iris 分类器

### 12.1 任务目标

用 scikit-learn 训练你的第一个分类模型，完整体验一次机器学习训练流程。

### 12.2 文件位置

建议创建：

```text
ai-learning/02-sklearn-projects/iris_classifier.py
```

### 12.3 任务要求

你需要完成以下步骤：

1. 导入依赖
2. 加载 iris 数据集
3. 打印数据形状
4. 打印特征名和标签名
5. 拆分训练集和测试集
6. 创建 LogisticRegression 模型
7. 训练模型
8. 在测试集上预测
9. 计算准确率
10. 打印 5 条预测结果和真实标签
11. 输出 classification report
12. 写 5 行总结，解释你观察到了什么

### 12.4 参考代码骨架

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


def main():
    iris = load_iris()

    X = iris.data
    y = iris.target

    print("Feature shape:", X.shape)
    print("Label shape:", y.shape)
    print("Feature names:", iris.feature_names)
    print("Target names:", iris.target_names)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

    print("\nSample predictions:")
    for i in range(5):
        pred_name = iris.target_names[y_pred[i]]
        true_name = iris.target_names[y_test[i]]
        print(f"Prediction: {pred_name}, Truth: {true_name}")

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, target_names=iris.target_names))


if __name__ == "__main__":
    main()
```

### 12.5 运行方式

```bash
python iris_classifier.py
```

### 12.6 你需要写下来的问题答案

运行完成后，在同目录创建 `iris_notes.md`，回答：

1. 这个任务的 feature 是什么？
2. label 是什么？
3. 为什么要用 `train_test_split`？
4. `test_size=0.2` 代表什么？
5. `random_state=42` 有什么用？
6. `stratify=y` 有什么用？
7. `model.fit` 做了什么？
8. `model.predict` 做了什么？
9. accuracy 是怎么计算的？
10. classification report 中 precision、recall、f1-score 分别是什么意思？

### 12.7 验收标准

完成后你应该有两个文件：

```text
iris_classifier.py
iris_notes.md
```

并且满足：

- 脚本可以正常运行
- 输出准确率
- 输出 5 条预测结果
- 输出 classification report
- 你能口头解释代码每一部分的作用

---

## 13. 每周复盘模板

每周结束时，写一份简短复盘：

```markdown
# 第 X 周复盘

## 本周完成

- 

## 我真正理解了什么

- 

## 我还不理解什么

- 

## 遇到的问题

- 

## 下周计划

- 
```

---

## 14. 推荐学习原则

1. 不要只看视频，每学一个概念都要写代码。
2. 不要急着训练大模型，先理解小模型训练流程。
3. 不要跳过数据处理，真实项目 60% 以上时间都在处理数据。
4. PyTorch 的训练循环必须手写多次，直到能默写。
5. 学 LLM 前先理解 tokenizer、embedding、attention。
6. RAG 和微调是两条不同路线，要分别练习。
7. Triton 是性能优化工具，不是 AI 入门工具；但如果你想做 AI Infra，它非常值得学。

---

## 15. 建议的第一个月计划

### 第 1 周

- Day 1：准备环境，跑通依赖检查
- Day 2：学习 feature、label、训练集、测试集
- Day 3：学习 NumPy array、shape、矩阵运算
- Day 4：学习 Pandas 读取和查看数据
- Day 5：完成 Titanic 数据探索前半部分
- Day 6：完成 Titanic 可视化
- Day 7：复盘

### 第 2 周

- Day 1：完成 Iris 分类器
- Day 2：理解 accuracy、precision、recall、f1
- Day 3：训练 Logistic Regression
- Day 4：训练 RandomForest
- Day 5：比较两个模型
- Day 6：完成 Titanic 生存预测
- Day 7：复盘

### 第 3 周

- Day 1：PyTorch tensor 基础
- Day 2：autograd
- Day 3：nn.Module
- Day 4：Dataset/DataLoader
- Day 5：手写训练循环
- Day 6：用 PyTorch 重写 Iris 分类器
- Day 7：复盘

### 第 4 周

- Day 1：加载 MNIST
- Day 2：定义 MLP
- Day 3：训练 MNIST
- Day 4：评估模型
- Day 5：可视化错误样本
- Day 6：整理项目 README
- Day 7：复盘
