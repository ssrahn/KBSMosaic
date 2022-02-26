import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

def get_data(file):

    data = pd.read_csv(file)

    feat_raw = data['board']
    label_raw = data['solution']

    feat = []
    label = []

    for i in feat_raw:
        data = i.split(',')
        x = np.array([int(j) for j in data]).reshape((9,9,1))
        feat.append(x)
    
    feat = np.array(feat)
    feat = (feat+1)/10
    feat -= .5    
    
    for i in label_raw:
        data = i.split(',')
        x = np.array([int(j) for j in data]).reshape((81,1))
        label.append(x)   
    
    label = np.array(label)

    del(feat_raw)
    del(label_raw)  

    x_train, x_test, y_train, y_test = train_test_split(feat, label, test_size=0.2, random_state=42)
    
    return x_train, x_test, y_train, y_test