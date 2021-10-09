
# -*- coding: utf-8 -*-
"""
Utils for neural style trransfer 
"""
import torch
from PIL import Image
import matplotlib.pyplot as plt

import torchvision.transforms as transforms

import numpy as np

def get_loader_and_unloader(imsize):
    loader = transforms.Compose([
        transforms.Resize((imsize, imsize)),  # scale imported image
        transforms.ToTensor()])  # transform it into a torch tensor

    unloader = transforms.ToPILImage()  # reconvert into PIL image
    return loader, unloader


def image_loader(image_name, transform, device = 'cpu'):
    image = Image.open(image_name)
    if image.mode=='L':
        image = Image.open(image_name).convert('RGB')
    # fake batch dimension required to fit network's input dimensions
    image = transform(image).unsqueeze(0)
    return image.to(device, torch.float)


def imshow(tensor, unloader, title=None):
    image = tensor.cpu().clone()  # we clone the tensor to not do changes on it
    image = image.squeeze(0)      # remove the fake batch dimension
    image = unloader(image)
    plt.imshow(image)
    if title is not None:
        plt.title(title)
    plt.pause(0.001) # pause a bit so that plots are updated


def reshape_original_size(original_image_path, new_image_tensor, unloader):
    print('\n ---- Reshape output image ---')
    original_img = Image.open(original_image_path).convert('RGB')
    plt.imshow(original_img)
    plt.show()
    print('Original shape:',np.array(original_img).shape)
    W, H = original_img.size
    Resize_img = transforms.Resize((H, W))
    new_image = unloader(Resize_img(new_image_tensor.cpu().clone().squeeze(0)))
    print("New outputshape:", np.array(new_image).shape)
    return new_image

