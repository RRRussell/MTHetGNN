# MTHetGNN
Multivariate time series forecasting using heterogeneous graph
This repository is the official implementation of [Modeling Complex Spatial Patterns with Temporal Features via Heterogeneous Graph Embedding Networks]()

## Requirements
- python 3.7.7
- Pytorch 1.4.0

To install requirements:

```setup
pip install -r requirements.txt
```

## Overview

#### Dataset

We conduct experiments on three benchmark datasets for multivariate time series forecasting tasks, this table shows dataset statistics

| Dataset      | T                  | D       | L          |
| -------------|--------------------| --------| -----------|
| Exchange_rate|7588                |    8    |  1 day     |
|              |                    |         |            |
| Solar        |52560               |    137  |  10 minutes|
|              |                    |         |            |
| Traffic      |17544               |    862  |  1 hour    |
|              |                    |         |            |

where `T` is the length of time series, `D` is the number of variables, `L` is the sample rate. Download the [dataset](https://drive.google.com/drive/folders/1xErmb8GIJVikL5CiSXv3bQTWkLAVbJyT?usp=sharing) and put them under `data` folder
 
#### Preprocessing
We split the raw data into `train set`, `validation set` and `test set`, in the ratio of 6:2:2. 

In each set, consecutive time series
with certain length of `window size` are sampled as a slice, which forms a forecasting unit. The slice window moves over the entire 
time series in the pace of 1 step each time 

#### Adjacency matrix

We use three adjacency matrix to model explicit relations among time series in both static and dynamic way. Casual inference matrix and correlation relation matrix can be calculated in following steps.

We use R to measure static casual inference between time series. To get the Casual inference matrix, run this code under `data` folder:

```TE matrix
Rscript rte.R
```
and place the result files under `TE` folder.

We also implement a python version of Casual inference measurement, run this code:
```TE matrix 2
python Teoriginal.py
```

We use `pandas` toolkit to get static correlations among time series. To get the Correlation matrix, run this code under `data` folder:

```CORR matrix
python corr.py
```
and place the result files under `TE` folder. 

## Training

To train the model(s) in the paper, run this code:

```train
python train.py --model MTHetNet --num_adjs 3 --channel_size 12 --hid1 40 --hid2 10
```

## Evaluation

To evaluate the model in the paper, run this code:

```eval
python eval.py --model_file model.pt --data data/exchange_rate.txt --horizon 5
```

## Pre-trained Models

You can download pre-trained models here:

- [MTHetGNN pre-trained model](https://drive.google.com/drive/folders/1ynmgFcDxAXZpVArbwon5EAXra_0JRExH?usp=sharing) trained on different datasets. 

and place the pre-trained model under `model` folder. Note that this model should be loaded directly with Pytorch,
or passed to `eval.py`.

On a 1070Ti, it took 2.6 seconds per epoch on Exchange_rate dataset, in the default setting of hyper parameters.



## Results

We train MTHetGNN for 100 epochs for each train option, and use the model that has the best performance on validation
set for test. 
 
We use three conventional evaluation metrics to evaluate the performance of MTHetGNN model: Mean Absolute Error(**MAE**),
Relative Absolute Error(**RAE**) and Empirical Correlation Coefficient(**CORR**), the following table shows the results:



| Model name| Dataset            | horizon | MAE    | RAE    | CORR   |
| ----------|--------------------| --------| -------| -------| -------|
||||||
|           |                    |    3    |  0.0173| 0.0132 | 0.9824 |
| MTHetGNN  |exchange_rate       |    6    |  0.0238| 0.0190 | 0.9746 |
|           |                    |    12   |  0.0327| 0.0266 | 0.9604 |
|           |                    |    24   |  0.0430| 0.0361 | 0.9415 |
||||||
|           |                    |    3    |  0.1668| 0.0788 | 0.9872 |
| MTHetGNN  |solar               |    6    |  0.2175| 0.1111 | 0.9772 |
|           |                    |    12   |  0.2872| 0.1514 | 0.9583 |
|           |                    |    24   |  0.3862| 0.2217 | 0.9210 |
||||||
|           |                    |    3    |  0.4142| 0.2349 | 0.8975 |
| MTHetGNN  |traffic             |    6    |  0.4303| 0.2490 | 0.8887 |
|           |                    |    12   |  0.4376| 0.2592 | 0.8828 |
|           |                    |    24   |  0.4500| 0.2661 | 0.8776 |

Examples with parameters to run different datasets are in `runExchangeRate.sh`, `runSolar.sh` and `runTraffic.sh`, in which specific hyperparameters for each training options are listed.
