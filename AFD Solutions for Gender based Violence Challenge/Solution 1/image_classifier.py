import pandas as pd

test = pd.read_csv(
    'data/landing_zone/GBV_Zindi_project/Datasets/Test/annos/test_annoations.csv',
    names=['class_name', 'Xmin', 'Ymin', 'weidth', 'height', 'image_id', 'imgW', 'imgH']
)
test.head()

Xmax = test['Xmin'] + test['weidth']
Ymax = test['Ymin'] + test['height']

test.insert(2, "Xmax", Xmax)
test.insert(4, "Ymax", Ymax)

first_column = test.pop('image_id')
test.insert(0, "image_id", first_column)
last_column = test.pop('class_name')

test.insert(5, "class_name ", last_column)
test["Xmin"] = test["Xmin"] / test["imgW"]
test["Xmax"] = test["Xmax"] / test["imgW"]

test.head()
test["Ymin"] = test["Ymin"] / test["imgH"]
test["Ymax"] = test["Ymax"] / test["imgH"]

test.head()
data_test = test.drop(["weidth", "height", "imgW", "imgH"], axis=1)
data_test.head()

data_test.to_csv('data/processed/gbv_images/Test/annos/test.csv', index=False)

train = pd.read_csv(
    'data/landing_zone/GBV_Zindi_Project/Datasets/Train/annos/train_annotations.csv',
    names=['class_name', 'Xmin', 'Ymin', 'weidth', 'height', 'image_id', 'imgW', 'imgH']
)
train.head()


Xmax=train['Xmin']+ train['weidth']
train.insert(2,"Xmax",Xmax)
Ymax=train['Ymin']+ train['height']
print(Ymax)
train.insert(4,"Ymax",Ymax)
first_column = train.pop('image_id')
train.insert(0,"image_id",first_column)
last_column = train.pop('class_name')
train.insert(5,"class_name ",last_column)
train.head()
train["Xmin"]=train["Xmin"]/train["imgW"]
train["Xmax"]=train["Xmax"]/train["imgW"]

train.head()
train["Ymin"]=train["Ymin"]/train["imgH"]
train["Ymax"]=train["Ymax"]/train["imgH"]

train.head()
data_train=train.drop(["weidth",	"height",	"imgW",	"imgH"],axis=1)
data_train.head()
data_train.to_csv('data/processed/gbv_images/Train/annos/train.csv',index=False )


import cv2
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import random
from skimage import io
from shutil import copyfile
import sys
import time

import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array