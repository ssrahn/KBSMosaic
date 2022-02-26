import sys
import copy
import numpy as np
from tensorflow import keras
from model import get_model
from dataGen import get_data

def norm(a):
    return (a/10)-.5

def denorm(a):
    return (a+.5)*10

def inference_mosaic(sample):
    feat = copy.copy(sample)
    out = model.predict(feat.reshape((1,9,9,1)))  
    out = out.squeeze()
    pred = np.argmax(out, axis=1).reshape((9,9))

    return pred

def test_accuracy(feats, labels):
    correct = 0
    for i,feat in enumerate(feats):
        pred = inference_mosaic(feat)        
        true = labels[i].reshape((9,9))     
        if(abs(true - pred).sum()==0):
            correct += 1
        
    print(correct/feats.shape[0])

def solve_mosaic(game):
    game = game.replace('\n', '')
    game = game.replace(' ', '')
    game = np.array([int(j) for j in game]).reshape((9,9,1))
    game = norm(game)
    game = inference_mosaic(game)
    return game


x_train, x_test, y_train, y_test = get_data('../instances/data.csv')

if len(sys.argv) > 1:
    model = keras.models.load_model(sys.argv[1])
else:
    model = get_model()

    adam = keras.optimizers.Adam(lr=.001)
    model.compile(loss='sparse_categorical_crossentropy', optimizer=adam)

    model.fit(x_train, y_train, batch_size=32, epochs=10)
    model.save('model.h5')

test_accuracy(x_test[:100], y_test[:100])