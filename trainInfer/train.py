import sys
sys.path.append('../neurASP/')
import time

import torch

from dataGen import dataList, obsList, train_loader, test_loader
from network import Sudoku_Net
from neurasp import NeurASP

startTime = time.time()

######################################
# The NeurASP program can be written in the scope of ''' Rules '''
######################################

board_size = 10
board_size_str = str(board_size)

dprogram = '''
% neural rule
nn(identify(81, img), [0,1,2,3,4,5,6,7,8,9,empty]).

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
# Define nnMapping and optimizers, initialze NeurASP object
########

m = Sudoku_Net()
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
for i in range(15):
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
