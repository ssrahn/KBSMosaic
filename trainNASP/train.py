import sys
sys.path.append('../neurASP/')
import time

import torch

from dataGen import dataList, obsList, train_loader, test_loader
from neurasp import NeurASP
from network import Sudoku_Net

startTime = time.time()

######################################
# The NeurASP program can be written in the scope of ''' Rules '''
# It can also be written in a file
######################################

dprogram = '''
% neural rule
nn(sol(81, config), [0,1,2,3,4,5,6,7,8,9]).

% Add each clue from the input image to our rule sets
clue(R,C,N) :- sol(Pos, config, N), R=Pos/9+1, C=Pos\9+1.

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
# Define nnMapping and optimizers, initialze NeurASP object
########

m = Sudoku_Net()
nnMapping = {'sol': m}
optimizers = {'sol': torch.optim.Adam(m.parameters(), lr=0.0001)}
NeurASPobj = NeurASP(dprogram, nnMapping, optimizers, gpu=True)

########
# Start training and testing
########

print('Initial test accuracy (whole board): {:0.2f}%\nInitial test accuracy (single cell): {:0.2f}%'.format(*NeurASPobj.testNN('sol', test_loader)))

for i in range(100):
    print('Training for Epoch {}...'.format(i+1))
    time1 = time.time()
    NeurASPobj.learn(dataList=dataList, obsList=obsList, epoch=1, smPickle='stableModels.pickle')
    time2 = time.time()
    acc, singleAcc = NeurASPobj.testNN('sol', train_loader)
    print('Train Acc (whole board): {:0.2f}%'.format(acc))
    print('Train Acc (single cell): {:0.2f}%'.format(singleAcc))
    acc, singleAcc = NeurASPobj.testNN('sol', test_loader)
    print('Test Acc (whole board): {:0.2f}%'.format(acc))
    print('Test Acc (single cell): {:0.2f}%'.format(singleAcc))
    print("--- train time: %s seconds ---" % (time2 - time1))
    print("--- test time: %s seconds ---" % (time.time() - time2))
    print('--- total time from beginning: %s minutes ---' % int((time.time() - startTime)/60) )
    
    saveModelPath = 'model/model_epoch{}.pt'.format(i+1)
    print('Storing the trained model into {}'.format(saveModelPath))
    torch.save(m.state_dict(), saveModelPath)
