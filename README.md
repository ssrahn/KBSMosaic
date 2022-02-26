# KBSMosaic
Educational project to solve mosaic instances with NeurASP

## Generator
```
python generator/mosaicGenerator <file path> <number of instances>
```
For example:
```
python generator/mosaicGenerator ../instances/ 10 (To create images and instance files)
python generator/mosaicGenerator instances/data.csv 10000 (To create csv file)
```

## Train NeurASP
To train a new model:
```
python trainNASP/train.py <optional number of data>
```
Trained model will be saved in root directory as model_dataXX.pt.

Test a given model:
```
python trainNASP/test.py
```

Use inference to get a solution:
```
python trainNASP/infer.py <IMAGE>
```

## Train a pure CNN
Needs a csv Dataset and will create a model.h5 file in the root directory.
If a model is given, it wont train a new one.
```
python trainNN/mosaic.py <dataset> <optional model>
```
