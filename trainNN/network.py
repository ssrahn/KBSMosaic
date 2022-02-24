from torch import nn
import torch.nn.functional as F

class Sudoku_Net(nn.Module):
    def __init__(self):
        super(Sudoku_Net, self).__init__()
        self.conv0 = nn.Conv2d(1, 512,kernel_size=3,stride=1,padding=1)
        self.conv1=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv2=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv3=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv4=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv5=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv6=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv7=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv8=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv9=nn.Conv2d(512,512,kernel_size=3,stride=1,padding=1)        
        self.conv1x1=nn.Conv2d(in_channels=512,out_channels=10,kernel_size=1)
        
    def forward(self, x_orig):
        print("Shape 0: ", x_orig.shape)  
        x=self.conv0(x_orig)
        x=F.relu(x)
        
        print("Shape 1: ", x_orig.shape)  
        x=self.conv1(x)
        x=F.relu(x)

        print("Shape 2: ", x_orig.shape)  
        x=self.conv2(x)
        x=F.relu(x)
        
        print("Shape 3: ", x_orig.shape)  
        x=self.conv3(x)
        x=F.relu(x)
        
        print("Shape 4: ", x_orig.shape)  
        x=self.conv4(x)
        x=F.relu(x)
        
        print("Shape 5: ", x_orig.shape)  
        x=self.conv5(x)
        x=F.relu(x)
        
        print("Shape 6: ", x_orig.shape)  
        x=self.conv6(x)
        x=F.relu(x)
        
        print("Shape 7: ", x_orig.shape)  
        x=self.conv7(x)
        x=F.relu(x)
        
        print("Shape 8: ", x_orig.shape)  
        x=self.conv8(x)
        x=F.relu(x)
        
        print("Shape 9: ", x_orig.shape)  
        x=self.conv9(x)
        x=F.relu(x)

        print("Shape 10: ", x_orig.shape)  
        x=self.conv1x1(x)

        print("Shape 11: ", x_orig.shape)  
        x=x.permute(0,2,3,1)

        print("Shape 12: ", x_orig.shape)  
        x=x.view(-1,81,10)

        print("Shape 13: ", x_orig.shape)  
        x=nn.Softmax(2)(x)

        print("Shape 14: ", x_orig.shape)  
        return x