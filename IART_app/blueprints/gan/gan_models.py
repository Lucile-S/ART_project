#%%
import torch
import torch.nn as nn
import os 
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from datetime import datetime
from torchvision.utils import save_image


Genre_classes = {
    'abstract': 0,
    'allegorical painting': 1, 
    'animal painting': 2, 
    'cityscape': 3, 
    'flower painting': 4, 
    'illustration': 5, 
    'interior': 6, 
    'landscape': 7, 
    'marina': 8, 
    'mythological painting': 9,
    'nude painting (nu)': 10, 
    'portrait': 11, 
    'religious painting': 12, 
    'self-portrait': 13, 
    'sketch and study': 14, 
    'still life': 15,
    'symbolic painting': 16}


Artist_classes ={
    'Amedeo Modigliani': 0, 
    'Arnold Bocklin': 1, 
    'Artemisia Gentileschi': 2, 
    'Claude Monet': 3,
    'David Burliuk': 4, 
    'Edward Hopper': 5,
    'Ernst Ludwig Kirchner': 6,
    'Gustav Klimt': 7,
    'Henri Matisse': 8,
    'Henri Rousseau': 9,
    'John James Audubon': 10,
    'Joseph Mallord William Turner': 11,
    'Katsushika Hokusai': 12,
    'Pablo Picasso': 13, 
    'Pierre Auguste Renoir': 14, 
    'Piet Mondrian': 15, 
    'Rembrandt': 16, 
    'Sandro Botticelli': 17, 
    'Theophile Steinlen': 18, 
    'Vassily Kandinsky': 19, 
    'Vincent Van Gogh': 20, 
    'Zdzislaw Beksinski': 21
    }

class Generator(nn.Module):
    def __init__(self, channels_noise, channels_img, features_g, num_classes, img_size, embed_size):
        super(Generator, self).__init__()
        self.img_size = img_size
        self.net = nn.Sequential(
            # Input: N x channels_noise x 1 x 1
            self._block(channels_noise + embed_size, features_g * 16, 4, 1, 0),  # img: 4x4
            self._block(features_g * 16, features_g * 8, 4, 2, 1),  # img: 8x8
            self._block(features_g * 8, features_g * 4, 4, 2, 1),  # img: 16x16
            self._block(features_g * 4, features_g * 2, 4, 2, 1),  # img: 32x32
            nn.ConvTranspose2d(
                features_g * 2, channels_img, kernel_size=4, stride=2, padding=1
            ),
            # Output: N x channels_img x 64 x 64
            nn.Tanh(),
        )
        self.embed = nn.Embedding(num_classes,embed_size)
        #self.embed = nn.Embedding(num_classes,num_classes)

    def _block(self, in_channels, out_channels, kernel_size, stride, padding):
        return nn.Sequential(
            nn.ConvTranspose2d(
                in_channels, out_channels, kernel_size, stride, padding, bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(),
        )

    def forward(self, x, labels):
        embedding = self.embed(labels).unsqueeze(2).unsqueeze(3)
        x = torch.cat([x, embedding], dim=1)
        return self.net(x)


def show_tensor_image(image_tensor, size=(1,64, 64), resize=False, show=True):
    '''
    Function for visualizing images: Given a tensor of images, number of images, and
    size per image, plots and prints the images in an uniform grid.
    '''
    image_tensor = (image_tensor + 1) / 2
    print(image_tensor.shape)
    image = image_tensor.detach().squeeze().permute(1, 2, 0).numpy()
    print(image.shape)
    if resize:
        image = transforms.Resize((128,128))(image)
    plt.imshow(image)
    if show:
        plt.show()
    

def denorm(img_tensors):
    stats = (0.5, 0.5, 0.5), (0.5, 0.5, 0.5)
    return img_tensors * stats[1][0] + stats[0][0]

# -- function to return key for any value
def get_key(my_dict,val):
    for key, value in my_dict.items():
         if val == value:
             return key
 

def run_gan(label:int, output_dir:str, by='by_artist'):
    # -- parameters 
    device = 'cpu'
    DIR = os.path.dirname(os.path.abspath(__file__))
    Z_DIM = 124
    CHANNELS_IMG = 3
    FEATURES_GEN = 64
    if by == 'by_artist':
        NUM_CLASSES = 22
        NUM_EPOCHS = 405
    if by == 'by_genre':
        NUM_CLASSES = 17
        NUM_EPOCHS = 3195
    IMG_SIZE = 64
    GENERATOR_EMBEDDING =  NUM_CLASSES 
    # -- generator 
    gen = Generator(Z_DIM, CHANNELS_IMG, FEATURES_GEN, NUM_CLASSES, IMG_SIZE, GENERATOR_EMBEDDING).to(device)
    # -- load weights
    if by == 'by_artist':
        ckpt_path  = os.path.join(DIR,'models',f'2021_08_26_WcGAN_BYARTIST_v1_{NUM_EPOCHS}_latest.pkl')
    if by == 'by_genre':
        ckpt_path  = os.path.join(DIR,'models',f'2021_08_20_WcGAN_BYGENRE_v1_{NUM_EPOCHS}_latest.pkl')
    ckpt = torch.load(ckpt_path, map_location=torch.device(device))
    gen.load_state_dict(ckpt['gen_state_dict'])
    # -- put the generator in evaluation mode 
    gen = gen.eval()
    # -- Changing the Class Vector
    noise = torch.randn(1 , Z_DIM, 1, 1).to(device)
    label_tensor = torch.tensor([label]).to(device)
    fake = gen(noise, label_tensor)
    show_tensor_image(fake)
    date = datetime.now().strftime("%d_%m_%Y-%I:%M:%S%f_%p")
    output_filename = f"GAN_{by}_label-{label}_{date}.png"
    save_image(denorm(transforms.Resize(256)(fake)).clamp(0, 1), os.path.join(output_dir, output_filename), nrow=1)
    return  output_filename



if __name__ ==  "__main__":
    label = 5
    print(f'Artist: {get_key(Artist_classes,label)}')
    run_gan(label,output_dir='.', by='artist')
    plt.show()


# %%
