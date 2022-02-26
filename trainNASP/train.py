import sys
sys.path.append('../neurASP/')
import time

import torch

from dataGen import dataList, obsList, train_loader, test_loader
from network import Mosaic_Net
from neurasp import NeurASP

startTime = time.time()

######################################
# The NeurASP program can be written in the scope of ''' Rules '''
######################################
dprogram = '''
% neural rule
nn(identify(81, img), [0,1,2,3,4,5,6,7,8,9,empty]).

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
# Define nnMapping and optimizers, initialze NeurASP object
########

m = Mosaic_Net()
nnMapping = {'identify': m}
optimizers = {'identify': torch.optim.Adam(m.parameters(), lr=0.0001)}
NeurASPobj = NeurASP(dprogram, nnMapping, optimizers)

########
# Set up the number of data to be used in training
########
try:
    numOfData = int(sys.argv[1])
except:
    numOfData = 25
dataList = dataList[:numOfData]
obsList = obsList[:numOfData]

########
# Start training from scratch and testing
########

saveModelPath = 'model_data{}.pt'.format(numOfData)

print('Use {} data to train the NN for 4000 epochs by NN only method (i.e., CrossEntropy loss)'.format(numOfData))
print(r'The identification accuracy of M_{identify} will also be printed out.\n')
for i in range(5):
    if i == 0:
        print('\nBefore Training ...')
    else:
        print('\nContinuously Training for 100 Epochs -- Round {} ...'.format(i))
        time1 = time.time()
        # here alpha=1 means rules are not used in training, in other words, it's usual NN training with cross entropy loss
        NeurASPobj.learn(dataList=dataList, obsList=obsList, alpha=1, epoch=100, lossFunc='cross')
        time2 = time.time()
        print("--- train time: %s seconds ---" % (time2 - time1))        

    acc, singleAcc = NeurASPobj.testNN('identify', train_loader)
    print('Train Acc Using Pure NN (whole board): {:0.2f}%'.format(acc))
    print('Train Acc Using Pure NN (single cell): {:0.2f}%'.format(singleAcc))
    acc, singleAcc = NeurASPobj.testNN('identify', test_loader)
    print('Test Acc Using Pure NN (whole board): {:0.2f}%'.format(acc))
    print('Test Acc Using Pure NN (single cell): {:0.2f}%'.format(singleAcc))
    print('--- total time from beginning: %s minutes ---' % int((time.time() - startTime)/60) )

# save the trained model
print('Storing the trained model into {}'.format(saveModelPath))
torch.save(m.state_dict(), saveModelPath)
