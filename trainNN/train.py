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

board_size = 9
board_size_str = str(board_size)
board_size_2d_str = str(board_size * board_size)

dprogram = '''
% neural rule
nn(sol(81, config), [0,1,2,3,4,5,6,7,8,9]).

% Add Position to our Rule Set to make it safe
pos(i) : i=0..(81).

% Add two versions to each set, one where coloring at position x,y is black = 1 or white = 0
coloring(x,y,0), coloring(x,y,1) :- pos(i), x=pos(i)/9, y=pos(i)\ 9.

% Add each restriction number from the input image to our rule sets
a(x,y,N) :- sol(Pos, config, N), x=Pos/9, y=Pos\ 9.

% Now, for each restricted number, look at its 3x3 Neighborhood (including itself) and add up all the colorings of their fields
% If the total number does not add up to the number demanded by the restricted field, then delete Set from our Valid Solution Set
:- a(x,y,N), 
 coloring(x+1,y+1, C1), coloring(x+1,y, C2), coloring(x+1,y-1, C3), 
 coloring(x, y+1, C4),  coloring(x,y, C5),   coloring(x,y-1, C6),
 coloring(x-1,y+1, C7), coloring(x-1,y, C8), coloring(x-1,y-1, C9),
 (C1 + C2 + C3 + C4 + C5 + C6 + C7 + C8 + C9) != N.
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
