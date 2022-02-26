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
    correct_whole = 0
    correct_cell = 0
    for i,feat in enumerate(feats):
        pred = inference_mosaic(feat)        
        true = labels[i].reshape((9,9))
        diff = abs(true - pred).sum()
        if(diff==0):
            correct_whole += 1
        correct_cell += (81-diff)/81
    
    return correct_whole/feats.shape[0], correct_cell/feats.shape[0]

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("usage: python mosaic.py <dataset> <optional model>")
        exit()
    
    x_train, x_test, y_train, y_test = get_data(sys.argv[1])

    if len(sys.argv) > 2:
        model = keras.models.load_model(sys.argv[2])
    else:
        model = get_model()

        adam = keras.optimizers.Adam(lr=.001)
        model.compile(loss='sparse_categorical_crossentropy', optimizer=adam)

        history = model.fit(x_train, y_train, batch_size=32, epochs=10)
        print("history:")
        print(history.history)
        model.save('model.h5')

    print("\nSummary:")
    print(model.summary())
    print("evaluation:")
    print("Loss:", model.evaluate(x_test, y_test))
    keras.utils.plot_model(model, "multi_input_and_output_model.png", show_shapes=True)
    acc_whole, acc_cell = test_accuracy(x_test[:100], y_test[:100])
    print("Acc whole board:", round(acc_whole,2))
    print("Acc single cell:", round(acc_cell,2))
