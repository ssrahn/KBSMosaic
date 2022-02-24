import sys
sys.path.append('../neurASP/')

import torch

from dataGen import dataListTest, obsListTest, test_loader
from neurasp import NeurASP
from network import Sudoku_Net

######################################
# The NeurASP program can be written in the scope of ''' Rules '''
######################################

dprogram = '''
% Add dynamic board size variables

% neural rule
nn(identify(81, img), [empty,0,1,2,3,4,5,6,7,8,9]).

% Add Position to our Rule Set to make it safe
pos(i) : i=0..(81).

% Add two versions to each set, one where coloring at position x,y is black = 1 or white = 0
coloring(x,y,0) : coloring(x,y,1) :- pos(i), x=pos(i)/9, y=pos(i)\ 9.

% Add each restriction number from the input image to our rule sets
restriction(x,y,N) :- identify(Pos, img, N), x=Pos/9, y=Pos\ 9, N!=empty.

% Now, for each restricted number, look at its 3x3 Neighborhood (including itself) and add up all the colorings of their fields
% If the total number does not add up to the number demanded by the restricted field, then delete Set from our Valid Solution Set
:- restricted(x,y,N), 
 coloring(x+1,y+1, C1), coloring(x+1,y, C2), coloring(x+1,y-1, C3), 
 coloring(x, y+1, C4),  coloring(x,y, C5),   coloring(x,y-1, C6),
 coloring(x-1,y+1, C7), coloring(x-1,y, C8), coloring(x-1,y-1, C9),
 (C1 + C2 + C3 + C4 + C5 + C6 + C7 + C8 + C9) != N.
'''

########
# Define nnMapping and initialze NeurASP object
########

m = Sudoku_Net()
nnMapping = {'identify': m}
NeurASPobj = NeurASP(dprogram, nnMapping, optimizers=None)

########
# Load pre-trained model and start testing
########

numOfData = [29]

for num in numOfData:
    print('\nLoad the model trained with {} data'.format(num))
    m.load_state_dict(torch.load('model_data{}.pt'.format(num), map_location='cpu'))

    # start testing
    acc, singleAcc = NeurASPobj.testNN('identify', test_loader)
    print('Test Acc Using Pure NN (whole board): {:0.2f}%'.format(acc))
    print('Test Acc Using Pure NN (single cell): {:0.2f}%'.format(singleAcc))
    acc = NeurASPobj.testInferenceResults(dataListTest, obsListTest)
    print('Test Acc Using NeurASP (whole board): {:0.2f}%'.format(acc))
