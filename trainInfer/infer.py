import sys
sys.path.append('../neurASP/')

import torch

from dataGen import loadImage
from network import Mosaik_Net
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
% Add each clue from the input image to our rule sets
clue(R,C,N) :- identify(Pos, img, N), R=Pos/9+1, C=Pos\9+1, N!=empty.

% Display the solution board where each cell is marked or unmarked, according to the clues
% Size of the solution board is larger, but without markings so that the following calculations also work for boundary conditions
marked(0,0..10,0).
marked(10,0..10,0).
marked(0..10,0,0).
marked(0..10,10,0).
% Add exactly one marking for each cell of the instance
1 {marked(R,C,M) : M=0..1} 1 :- R=P/9+1, C=P\9+1, P=0..80.

% Now, for each clue, look at its 3x3 Neighborhood (including itself) and add up all the markings of their fields
% If the total number does not add up to the number demanded by the clue, then delete Set from our Valid Solution Set
:- clue(R,C,N), 
 marked(R+1,C+1, M1), marked(R+1,C, M2), marked(R+1,C-1, M3), 
 marked(R, C+1, M4),  marked(R,C, M5),   marked(R,C-1, M6),
 marked(R-1,C+1, M7), marked(R-1,C, M8), marked(R-1,C-1, M9),
 (M1+M2+M3+M4+M5+M6+M7+M8+M9)!=N.
'''

########
# Define nnMapping and initialze NeurASP object
########

m = Mosaik_Net()
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
print('\nInference Result:\n', models[0])

########
# Read Solution from Model and print it
########

clues = [[-1]*9 for _ in range(9)]
solved = [[-5]*11 for _ in range(11)]
for model in models[0]:
    if "clue" in model:
        clue = [int(i) for i in model[5:-1].split(',')]
        clues[clue[0]-1][clue[1]-1] = clue[2]
    elif "marked" in model:
        mark = [int(i) for i in model[7:-1].split(',')]
        solved[mark[0]][mark[1]] = mark[2]
print("Board detected:")
print(np.array(clues))
print("Board Solution:")
print(np.array(solved)[1:10,1:10])
