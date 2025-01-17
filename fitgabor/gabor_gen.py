import torch
from torch import nn
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

torch.pi = torch.acos(torch.zeros(1)).item() * 2 # which is 3.1415927410125732

def gen_gabor(theta, sigma, Lambda, psi, gamma, center, image_size):
    
    sigma_x = sigma
    sigma_y = sigma / gamma

    ny, nx = image_size
    (y, x) = torch.meshgrid(torch.linspace(-1, 1, ny), torch.linspace(-1, 1, nx))
    x = x.unsqueeze(0).to(device)
    y = y.unsqueeze(0).to(device)
    print(x.shape)
    print(center.shape)
    print(theta.shape)
    # Rotation
    x_theta = (x - center[:,0].unsqueeze(-1)) * torch.cos(theta) + (y - center[:,1].unsqueeze(-1)) * torch.sin(theta)
    y_theta = -(x - center[:,0]) * torch.sin(theta) + (y - center[:,1]) * torch.cos(theta)

    gb = torch.exp(-.5 * (x_theta ** 2 / sigma_x ** 2 + y_theta ** 2 / sigma_y ** 2)) * torch.cos(2 * torch.pi / Lambda * x_theta + psi)
    
    return gb

class GaborGenerator(nn.Module):
    def __init__(self, image_size):
        """
        Gabor generator class.
        Params:
            theta (float): Orientation of the sinusoid (in ratian).
            sigma (float): std deviation of the Gaussian.
            Lambda (float): Sinusoid wavelengh (1/frequency).
            psi (float): Phase of the sinusoid.
            gamma (float): The ratio between sigma in x-dim over sigma in y-dim (acts
                like an aspect ratio of the Gaussian).
            center (tuple of integers): The position of the filter.
            image_size (tuple of integers): Image height and width.
        Returns:
            2D torch.tensor: A gabor filter.
        """
        
        super().__init__()
        self.theta = nn.Parameter(torch.rand(3,1))# * 4*torch.pi - 2*torch.pi).to(device))
        self.sigma = nn.Parameter(3*torch.ones(3,1))# * .05 + .15).to(device))
        self.Lambda = nn.Parameter(2*torch.ones(3,1))# * .2 + .5).to(device))
        self.psi = nn.Parameter(torch.rand(3,1))#*torch.pi/2).to(device)) 
        self.gamma = nn.Parameter(torch.ones(3,1))#+1.).to(device))
        self.center = nn.Parameter(torch.zeros(3,2))
        self.image_size = image_size
    
    def forward(self):
        # clip values in reasonable range
        # self.theta.data.clamp_(-2*torch.pi, 2*torch.pi)
        # self.sigma.data.clamp_(.13, 1)
        # self.Lambda.data.clamp_(.2, 2.)
        # self.center.data.clamp_(-.8, .8)
        gb = gen_gabor(self.theta, self.sigma, self.Lambda, self.psi, self.gamma, self.center, self.image_size)
        return gb.view(1, 1, *self.image_size)
    
    def apply_changes(self):
        self.sigma.requires_grad_(True)
