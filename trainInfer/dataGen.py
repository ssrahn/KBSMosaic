import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
from torchvision.transforms import transforms
from sklearn.model_selection import ShuffleSplit
from PIL import Image

class Mosaik_dataset(Dataset): 
    def __init__(self, file_path, transform=None, data_limit=99999):
        self.transform = transform
        self.image_dict = {}
        self.label_dict = {}

        for filename in os.listdir(file_path):
            path = os.path.join(file_path, filename)
            if "instance" in filename:
                f = os.path.splitext(filename)[0]+".png"
                if ".png" in filename:
                    im_frame = Image.open(path)
                    self.image_dict[f] = np.array(im_frame)
                else:
                    self.label_dict[f] = np.genfromtxt(path, delimiter=" ")
        
        keys_to_delete=[]
        keep_first_n=data_limit
        for i,key in enumerate(self.label_dict):
            if i>keep_first_n:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del self.label_dict[key]
        
        self.indices=np.arange(len(self.label_dict))
        self.idx_to_filename = {key:value for key,value in enumerate(self.label_dict.keys())}

    def __len__(self):
        return len(self.indices)
 
    def __getitem__(self, idx):
        filename=self.idx_to_filename[idx]
        x=self.image_dict[filename]
        x=torch.from_numpy(x).permute(2,0,1).float()
        y=self.label_dict[filename]
        if self.transform:
            x = self.transform(x)
        return x,y
    
def loadImage(path):
    im_frame = Image.open(path)
    np_frame = np.array(im_frame)
    tensor_img = torch.from_numpy(np_frame).permute(2,0,1).float()
    tensor_img = preprocessing(tensor_img).unsqueeze(0)
    return tensor_img

# initialze the dataset
file_path = '../instances/'

preprocessing = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Grayscale(),
            transforms.Resize((250,250)), #resize images
            transforms.ToTensor(),
            transforms.Normalize([.5],[.5])
            ])

dataset = Mosaik_dataset(file_path, preprocessing, data_limit=200)

# obtain the training and testing data
X_unshuffled = dataset.indices
train_ind=[]
test_ind=[]
rs = ShuffleSplit(n_splits=1, test_size=75, random_state=15)
rs.get_n_splits(X_unshuffled) 
for train_index, test_index in rs.split(X_unshuffled):
    train_ind.append(train_index)
    test_ind.append(test_index)

train_sampler = SubsetRandomSampler(train_ind[0].tolist())
test_sampler = SubsetRandomSampler(test_ind[0].tolist())
train_loader = DataLoader(dataset, batch_size=1, sampler=train_sampler)
test_loader = DataLoader(dataset, batch_size=64, sampler=test_sampler)
test_loader_inference = DataLoader(dataset, batch_size=1, sampler=test_sampler)

# construct dataList and obsList for training
dataList = []
obsList = []
for X, y in train_loader:
    tmp = (X, {'identify': y})
    dataList.append({'img': tmp})
    obsList.append('')

# construct dataListTest and obsListTest for testing the inference mode
dataListTest = []
obsListTest = []
for X, y in test_loader_inference:
    dataListTest.append({'img': X})
    obs = ''
    for Pos, value in enumerate(y.view(-1).tolist()):
        obs += ':- not identify({}, img, empty).\n'.format(Pos) if value == 0 else ':- not identify({}, img, {}).\n'.format(Pos, value)
    obsListTest.append(obs)