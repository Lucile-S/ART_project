# %%
"""
Neural Style Transfer using Pytorch
from https://pytorch.org/tutorials/advanced/neural_style_tutorial.html
This is  an implementation of the Neural-Style algorithm developed 
by Leon A. Gatys, Alexander S. Ecker and Matthias Bethge. 
"""
from __future__ import print_function

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from datetime import datetime

from PIL import Image
import matplotlib.pyplot as plt

import torchvision.transforms as transforms
import torchvision.models as torch_models

import copy
import os 
import time
import numpy as np
import blueprints.style_transfer.style_transfer_utils as utils
from blueprints.style_transfer.models import  get_input_optimizer, get_style_model_and_losses, VGG19


#import style_transfer_utils as utils
#from models import  get_input_optimizer, get_style_model_and_losses
#, VGG19


def run_style_transfer_app(content_path, style_path, output_dir, num_steps=500):
    """Run the style transfer."""
    DIR = os.path.dirname(os.path.abspath(__file__))
    # -- parameters
    t0 = time.time()
    num_steps = num_steps
    style_weight= 0.8e6
    content_weight= 1
    # -- device 
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # -- desired size of the output image
    imsize = 512 if torch.cuda.is_available() else 224 # use small size if no gpu
    # -- loader and unloader
    loader, unloader = utils.get_loader_and_unloader(imsize)

    # -- images
    content_img = utils.image_loader(content_path, loader, device=device)
    content_name = os.path.basename(content_path).split('.')[0]
    style_img = utils.image_loader(style_path, loader, device=device)
    style_name = os.path.basename(style_path).split('.')[0]

    # -- define cnn
    model_DIR = os.path.join(DIR, 'models')
    # try:
    #     cnn = torch_models.vgg19(pretrained=True).features.to(device).eval()
    # except:
    cnn= torch_models.vgg19(pretrained=True).features.to(device).eval()
    #cnn = VGG19(vgg_path=os.path.join(model_DIR, 'vgg19-dcbb9e9d.pth')).features.to(device).eval()
    print('---cnn---')
    print(cnn)

    # -- copy of the content image
    input_img = content_img.clone()
    # -- set up mean and std (imagenet values)
    normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(device)
    normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(device)
    
    print('Building the style transfer model..')
    model, style_losses, content_losses = get_style_model_and_losses(cnn,
        normalization_mean, normalization_std, style_img, content_img,device=device)
    optimizer = get_input_optimizer(input_img)

    print('Optimizing..')
    run = [0]
    while run[0] <= num_steps:

        def closure():
            # correct the values of updated input image
            input_img.data.clamp_(0, 1)

            optimizer.zero_grad()
            model(input_img)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.loss
            for cl in content_losses:
                content_score += cl.loss

            style_score *= style_weight
            content_score *= content_weight

            loss = style_score + content_score
            loss.backward()

            run[0] += 1
            if run[0] % 50 == 0:
                print("run {}:".format(run))
                print('Style Loss : {:4f} Content Loss: {:4f}'.format(
                    style_score.item(), content_score.item()))
                print()
                utils.imshow(input_img, unloader, title=f'image run {run[0]}')
                plt.show()

            return style_score + content_score

        optimizer.step(closure)
        
    # a last correction...
    input_img.data.clamp_(0, 1)
    # -- reshape output image to its original shape
    new_image = utils.reshape_original_size(content_path,input_img, unloader)
    # -- Save the final image to output dir 

    date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
    output_filename = f"{content_name}_{style_name}_{date}_steps_{num_steps}.png"
    output_path = os.path.join(output_dir, output_filename)
    new_image.save(output_path)
    print(f'Elapsed time :  {(time.time() - t0)/60} min')
    return  output_filename

if __name__ == "__main__":
    num_steps = 500

    #content_path = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/content/medusa.jpg'
    content_path = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/content/bird.jpg'
    #style_path = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/style/house-in-the-garden-1908.jpg'
    style_path = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/style/wave.jpg'
    output_dir = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/output'
    run_style_transfer_app(content_path, style_path, output_dir, num_steps=num_steps)



# %%
