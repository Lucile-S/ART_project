# -- visualize feature maps
#%%
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
import torchvision.models as torch_models
import copy 
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# ref : https://androidkt.com/how-to-visualize-feature-maps-in-convolutional-neural-networks-using-pytorch/


loader = transforms.Compose([
        transforms.Resize((224, 224)),  # scale imported image
        transforms.ToTensor(),
       ])

normalize =  transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
unloader = transforms.ToPILImage() 

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
    plt.show()
    if title is not None:
        plt.title(title)
    plt.pause(0.001) # pause a bit so that plots are updated

stats = (0.485, 0.456, 0.406), (0.229, 0.224, 0.225)
def denorm(img_tensors, stats=stats):
    return img_tensors * stats[1][0] + stats[0][0]


cnn= torch_models.vgg19(pretrained=True)
content_path = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/content/venise.jpg'
style_path = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/style/house-in-the-garden-1908.jpg'
output_dir = '/home/lucile/Projet_final/app/blueprints/style_transfer/images/output'


 
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.RandomResizedCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def loader_2(img_path):
    img = cv.imread(img_path)
    plt.imshow(img)
    plt.show()
    img=np.array(img)
    img=transform(img)
    img=img.unsqueeze(0)
    print(img.size())
    return img

print('-------------content-----------------')
content_img = image_loader(content_path, loader)
print(content_img.shape)
imshow(content_img, unloader, title=None)

 
print('-------------Style-----------------')
style_img = image_loader(style_path, loader)
print(style_img.shape)
imshow(style_img, unloader, title=None)


no_of_layers=0
conv_layers=[]
 
print('------------------Model--------------------')
model_children=list(cnn.children())
print(model_children)
 
for child in model_children:
  if type(child)==nn.Conv2d:
    no_of_layers+=1
    conv_layers.append(child)
  elif type(child)==nn.Sequential:
    for layer in child.children():
      if type(layer)==nn.Conv2d:
        no_of_layers+=1
        conv_layers.append(layer)
print('no_of_layer', no_of_layers)



print('------------------Conv layers--------------------')
results = [conv_layers[0](normalize(content_img))]
for i in range(1, len(conv_layers)):
    results.append(conv_layers[i](results[-1]))
outputs = results[:]

print('output lenght',len(outputs))


print('--------------Visualizing the Feature Maps------------------')
for num_layer in range(len(outputs)):
    plt.figure(figsize=(50, 10))
    layer_viz = outputs[num_layer][0, :, :, :]
    layer_viz = layer_viz.data
    print("Layer ",num_layer+1)
    for i, filter in enumerate(layer_viz):
        if i == 3: 
            break
        plt.subplot(2, 8, i + 1)
        plt.imshow(filter, cmap='gray')
        plt.axis("off")
    plt.show()
    plt.close()


results = [conv_layers[0](normalize(style_img))]
for i in range(1, len(conv_layers)):
    results.append(conv_layers[i](results[-1]))
outputs = results[:]

for num_layer in range(len(outputs)):
    plt.figure(figsize=(50, 10))
    layer_viz = outputs[num_layer][0, :, :, :]
    layer_viz = layer_viz.data
    print("Layer ",num_layer+1)
    for i, filter in enumerate(layer_viz):
        if i == 3: 
            break
        plt.subplot(2, 8, i + 1)
        plt.imshow(filter, cmap='gray')
        plt.axis("off")
    plt.show()
    plt.close()


print('---finish----')
# %%

# %%
