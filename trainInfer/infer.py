import sys
sys.path.append('../neurASP/')

import torch

from dataGen import loadImage
from network import Sudoku_Net
from neurasp import NeurASP
import numpy as np

######################################
# The NeurASP program can be written in the scope of ''' Rules '''
######################################

dprogram = '''
% neural rule
nn(identify(81, img), [0,1,2,3,4,5,6,7,8,9,empty]).
'''

rules = '''
% we assign one number at each position (R,C)
clue(R,C,N) :- identify(Pos, img, N), R=Pos/9, C=Pos\9, N!=empty.
1 {marked(R,C,M): M=0..1} 1 :- R=P/9, C=P\9, P=0..80.

:- clue(R,C,N), marked(R-1,C-1,M1), marked(R,C-1,M2), marked(R+1,C-1,M3), 
        marked(R-1,C,M4), marked(R,C,M5), marked(R+1,C,M6),
        marked(R-1,C+1,M7), marked(R,C+1,M8), marked(R+1,C+1,M9),
        (M1+M2+M3+M4+M5+M6+M7+M8+M9)==N, R>0, R<80, C>0, C<80.

:- clue(0,0,N), marked(0,0,M1), marked(1,0,M2), marked(0,1,M3), marked(1,1,M4),
        (M1+M2+M3+M4)==N.

:- clue(0,80,N), marked(0,80,M1), marked(1,80,M2), marked(0,79,M3), marked(1,79,M4),
        (M1+M2+M3+M4)==N.

:- clue(80,0,N), marked(80,0,M1), marked(80,1,M2), marked(79,0,M3), marked(79,1,M4),
        (M1+M2+M3+M4)==N.

:- clue(80,80,N), marked(80,80,M1), marked(79,80,M2), marked(80,79,M3), marked(79,79,M4),
        (M1+M2+M3+M4)==N.

:- clue(0,C,N), marked(0,C-1,M1), marked(0,C,M2), marked(0,C+1,M3),
        marked(1,C-1,M4), marked(1,C,M5), marked(1,C+1,M6),
        (M1+M2+M3+M4+M5+M6)==N, C>0, C<80.

:- clue(80,C,N), marked(80,C-1,M1), marked(80,C,M2), marked(80,C+1,M3),
        marked(79,C-1,M4), marked(79,C,M5), marked(79,C+1,M6),
        (M1+M2+M3+M4+M5+M6)==N, C>0, C<80.

:- clue(R,0,N), marked(R-1,0,M1), marked(R,0,M2), marked(R+1,0,M3),
        marked(R-1,1,M4), marked(R,1,M5), marked(R+1,1,M6),
        (M1+M2+M3+M4+M5+M6)==N, R>0, R<80.

:- clue(R,80,N), marked(R-1,80,M1), marked(R,80,M2), marked(R+1,80,M3),
        marked(R-1,79,M4), marked(R,79,M5), marked(R+1,79,M6),
        (M1+M2+M3+M4+M5+M6)==N, R>0, R<80.
'''

########
# Define nnMapping and initialze NeurASP object
########

m = Sudoku_Net()
nnMapping = {'identify': m}
NeurASPobj = NeurASP(dprogram, nnMapping, optimizers=None)

########
# Obtain the type of Sudoku and the path to the image from command line arguments
########
try:
    imagePath = sys.argv[1]
except:
    print('Error: please make sure your command follows the format: python infer.py IMAGE')
    sys.exit()

try:
    image = loadImage(imagePath)
except:
    print('Error: cannot load the image')
    sys.exit()

########
# Load pre-trained model
########

numOfData = 25
saveModelPath = 'model_data{}.pt'.format(numOfData)
print('\nLoad the model trained with {} instances of normal Sudoku puzzles'.format(numOfData))
m.load_state_dict(torch.load('model_data{}.pt'.format(numOfData), map_location='cpu'))

########
# Start infering on the given image
########

dataDic = {'img': image}
models = NeurASPobj.infer(dataDic=dataDic, mvpp=rules)
#print('\nInference Result:\n', models[0])

clues = [[-1]*9 for _ in range(9)]
solved = [[0]*9 for _ in range(9)]
for model in models[0]:
    if "clue" in model:
        clue = [int(i) for i in model[5:-1].split(',')]
        clues[clue[0]][clue[1]] = clue[2]
    elif "marked" in model:
        mark = [int(i) for i in model[7:-1].split(',')]
        solved[mark[0]][mark[1]] = mark[2]
print("Board detected:")
print(np.array(clues))
print("Board Solution:")
print(np.array(solved))
