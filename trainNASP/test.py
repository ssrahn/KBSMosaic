import sys
sys.path.append('../neurASP/')

import torch

from dataGen import dataListTest, obsListTest, test_loader
from neurasp import NeurASP
from network import Mosaic_Net

######################################
# The NeurASP program can be written in the scope of ''' Rules '''
######################################

dprogram = '''
% neural rule
nn(identify(81, img), [0,1,2,3,4,5,6,7,8,9]).

% Add each clue from the input image to our rule sets
clue(R,C,N) :- identify(Pos, img, N), R=Pos/9+1, C=Pos\9+1.

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

m = Mosaic_Net()
nnMapping = {'identify': m}
NeurASPobj = NeurASP(dprogram, nnMapping, optimizers=None)

########
# Load pre-trained model and start testing
########

numOfData = [25]

for num in numOfData:
    print('\nLoad the model trained with {} data'.format(num))
    m.load_state_dict(torch.load('model_data{}.pt'.format(num), map_location='cpu'))

    # start testing
    acc, singleAcc = NeurASPobj.testNN('identify', test_loader)
    print('Test Acc Using Pure NN (whole board): {:0.2f}%'.format(acc))
    print('Test Acc Using Pure NN (single cell): {:0.2f}%'.format(singleAcc))
    acc = NeurASPobj.testInferenceResults(dataListTest, obsListTest)
    print('Test Acc Using NeurASP (whole board): {:0.2f}%'.format(acc))
