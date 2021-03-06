import math
import torch
from torch import nn
import torch.nn.functional as F
from .crf import *

class SCNN(nn.Module):
    def __init__(self):
        super(SCNN, self).__init__()
        
        self.conv1_1 = nn.Conv2d(3, 64, 3, padding=1, bias=False)
        self.bn1_1 = nn.BatchNorm2d(64)
        self.conv1_2 = nn.Conv2d(64, 64, 3, padding=1, bias=False)
        self.bn1_2 = nn.BatchNorm2d(64)
        
        self.conv2_1 = nn.Conv2d(64, 128, 3, padding=1, bias=False)
        self.bn2_1 = nn.BatchNorm2d(128)
        self.conv2_2 = nn.Conv2d(128, 128, 3, padding=1, bias=False)
        self.bn2_2 = nn.BatchNorm2d(128)
        
        self.conv3_1 = nn.Conv2d(128, 256, 3, padding=1, bias=False)
        self.bn3_1 = nn.BatchNorm2d(256)
        self.conv3_2 = nn.Conv2d(256, 256, 3, padding=1, bias=False)
        self.bn3_2 = nn.BatchNorm2d(256)
        self.conv3_3 = nn.Conv2d(256, 256, 3, padding=1, bias=False)
        self.bn3_3 = nn.BatchNorm2d(256)
        
        self.conv4_1 = nn.Conv2d(256, 512, 3, padding=1, bias=False)
        self.bn4_1 = nn.BatchNorm2d(512)
        self.conv4_2 = nn.Conv2d(512, 512, 3, padding=1, bias=False)
        self.bn4_2 = nn.BatchNorm2d(512)
        self.conv4_3 = nn.Conv2d(512, 512, 3, padding=1, bias=False)
        self.bn4_3 = nn.BatchNorm2d(512)
        
        self.conv5_1 = nn.Conv2d(512, 512, 3, padding=2, dilation=2, bias=False)
        self.bn5_1 = nn.BatchNorm2d(512)
        self.conv5_2 = nn.Conv2d(512, 512, 3, padding=2, dilation=2, bias=False)
        self.bn5_2 = nn.BatchNorm2d(512)
        self.conv5_3 = nn.Conv2d(512, 512, 3, padding=2, dilation=2, bias=False)
        self.bn5_3 = nn.BatchNorm2d(512)
        
        self.conv6 = nn.Conv2d(512, 1024, 3, padding=4, dilation=4, bias=False)
        self.bn6 = nn.BatchNorm2d(1024)
        
        self.conv7 = nn.Conv2d(1024, 128, 1, bias=False)
        self.bn7 = nn.BatchNorm2d(128)
        
        self.conv_d = nn.Conv2d(128, 128, (1, 9), padding=(0, 4), bias=False)
        self.conv_u = nn.Conv2d(128, 128, (1, 9), padding=(0, 4), bias=False)
        self.conv_r = nn.Conv2d(128, 128, (9, 1), padding=(4, 0), bias=False)
        self.conv_l = nn.Conv2d(128, 128, (9, 1), padding=(4, 0), bias=False)
        
        self.conv8 = nn.Conv2d(128, 5, 1)
        
        self.fc9 = nn.Linear(5*18*50, 128)
        self.fc10 = nn.Linear(128, 4)
        
        # init weight and bias
        # for m in self.modules():
        #     if isinstance(m, nn.Conv2d):
        #         torch.nn.init.xavier_normal_(m.weight, gain=1)
        #     elif isinstance(m, nn.BatchNorm2d):
        #         m.weight.data.normal_(0, 1)
        #         m.bias.data.fill_(0)
        #     elif isinstance(m, nn.ConvTranspose2d):
        #         assert (m.weight.data.shape[2] == m.weight.data.shape[3])
        #         f = math.ceil(m.weight.data.shape[3] / 2)
        #         c = (2 * f - 1 - f % 2) / (2 * f)
        #         for i in range(m.weight.data.shape[2]):
        #             for j in range(m.weight.data.shape[3]):
        #                 m.weight.data[:, :, i, j] = (1 - abs(i / f - c)) * (1 - abs(j / f - c))
        #         m.bias.data.fill_(0)
        #
        # nn.init.normal_(self.conv_d.weight, mean=0, std=math.sqrt(2.5 / self.conv_d.weight.numel()))
        # nn.init.normal_(self.conv_u.weight, mean=0, std=math.sqrt(2.5 / self.conv_u.weight.numel()))
        # nn.init.normal_(self.conv_r.weight, mean=0, std=math.sqrt(2.5 / self.conv_r.weight.numel()))
        # nn.init.normal_(self.conv_l.weight, mean=0, std=math.sqrt(2.5 / self.conv_l.weight.numel()))
    
    def forward(self, x):
        x = F.relu(self.bn1_1(self.conv1_1(x)))
        x = F.relu(self.bn1_2(self.conv1_2(x)))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        x = F.relu(self.bn2_1(self.conv2_1(x)))
        x = F.relu(self.bn2_2(self.conv2_2(x)))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        x = F.relu(self.bn3_1(self.conv3_1(x)))
        x = F.relu(self.bn3_2(self.conv3_2(x)))
        x = F.relu(self.bn3_3(self.conv3_3(x)))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        x = F.relu(self.bn4_1(self.conv4_1(x)))
        x = F.relu(self.bn4_2(self.conv4_2(x)))
        x = F.relu(self.bn4_3(self.conv4_3(x)))
        
        x = F.relu(self.bn5_1(self.conv5_1(x)))
        x = F.relu(self.bn5_2(self.conv5_2(x)))
        x = F.relu(self.bn5_3(self.conv5_3(x)))
        
        x = F.relu(self.bn6(self.conv6(x)))
        x = F.relu(self.bn7(self.conv7(x)))
        
        for i in range(1, x.shape[2]):
            x[..., i:i+1, :].add_(F.relu(self.conv_d(x[..., i-1:i, :])))
        
        for i in range(x.shape[2] - 2, 0, -1):
            x[..., i:i+1, :].add_(F.relu(self.conv_u(x[..., i+1:i+2, :])))
        
        for i in range(1, x.shape[3]):
            x[..., i:i+1].add_(F.relu(self.conv_r(x[..., i-1:i])))
        
        for i in range(x.shape[3] - 2, 0, -1):
            x[..., i:i+1].add_(F.relu(self.conv_l(x[..., i+1:i+2])))
        
        x = F.dropout2d(x, p=0.1)
        
        x = self.conv8(x)
        x1 = x.clone()
        x2 = x.clone()
        
        x1 = F.interpolate(x1, size=[288, 800], mode='bilinear', align_corners=True)
        x1 = F.softmax(x1, dim=1)
        x2 = F.softmax(x2, dim=1)
        x2 = F.avg_pool2d(x2, 2, stride=2, padding=0)
        x2 = x2.view(-1, x2.numel() // x2.shape[0])
        x2 = self.fc9(x2)
        x2 = F.relu(x2)
        x2 = self.fc10(x2)
        x2 = torch.sigmoid(x2)
        
        return x1, x2


class CRFasRNN(nn.Module):
    def __init__(self):
        super(CRFasRNN, self).__init__()
        # input_dim: 1
        # input_dim: 3
        # input_dim: 500
        # input_dim: 500
        self.conv1_1 = nn.Conv2d(3, 64, 3, padding=100)
        self.conv1_2 = nn.Conv2d(64, 64, 3, padding=1)
        
        self.conv2_1 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv2_2 = nn.Conv2d(128, 128, 3, padding=1)
        
        self.conv3_1 = nn.Conv2d(128, 256, 3, padding=1)
        self.conv3_2 = nn.Conv2d(256, 256, 3, padding=1)
        self.conv3_3 = nn.Conv2d(256, 256, 3, padding=1)
        
        self.conv4_1 = nn.Conv2d(256, 512, 3, padding=1)
        self.conv4_2 = nn.Conv2d(512, 512, 3, padding=1)
        self.conv4_3 = nn.Conv2d(512, 512, 3, padding=1)

        self.conv5_1 = nn.Conv2d(256, 512, 3, padding=1)
        self.conv5_2 = nn.Conv2d(512, 512, 3, padding=1)
        self.conv5_3 = nn.Conv2d(512, 512, 3, padding=1)
        
        self.fc6 = nn.Conv2d(512, 4096, 7)
        self.fc7 = nn.Conv2d(4096, 4096, 1)

        self.conv_fr = nn.Conv2d(4096, 21, 1)
        self.deconv1 = nn.ConvTranspose2d(21, 21, 4, stride=2)
        
        self.conv_p4 = nn.Conv2d(512, 21, 1)
        self.deconv2 = nn.ConvTranspose2d(21, 21, 4, stride=2, bias=False)
        
        self.conv_p3 = nn.Conv2d(256, 21, 1)
        self.deconv3 = nn.ConvTranspose2d(21, 21, 16, stride=8, bias=False)
        
        self.crf = MultiStageMeanField()
        
    
    def cropAs(self, t1, t2):
        assert (t1.dim() == 4 and t2.dim() == 4)
        index = torch.zeros(4, 2, dtype=torch.int8)
        for i in range(4):
            s1, s2 = t1.shape[i], t2.shape[i]
            assert (s1 >= s2)
            index[i, 0] = (s1 - s2) // 2
            index[i, 1] = s2 - index[i, 0]
        return t1[index[0,0]:index[0,1], index[1,0]:index[1:1],
                  index[2,0]:index[2:1], index[3:0]:index[3:1]]
        
    def forward(self, x):
        data = x.clone()
        
        x = F.relu(self.conv1_1(x))
        x = F.relu(self.conv1_2(x))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        x = F.relu(self.conv2_1(x))
        x = F.relu(self.conv2_2(x))
        x = F.max_pool2d(x, 2, stride=2, padding=0)

        x = F.relu(self.conv3_1(x))
        x = F.relu(self.conv3_2(x))
        x = F.relu(self.conv3_3(x))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        pool3 = x.clone()

        x = F.relu(self.conv4_1(x))
        x = F.relu(self.conv4_2(x))
        x = F.relu(self.conv4_3(x))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        pool4 = x.clone()

        x = F.relu(self.conv5_1(x))
        x = F.relu(self.conv5_2(x))
        x = F.relu(self.conv5_3(x))
        x = F.max_pool2d(x, 2, stride=2, padding=0)
        
        x = F.relu(self.fc6(x))
        x = F.dropout2d(x, p=0.5)
        x = F.relu(self.fc7(x))
        x = F.dropout2d(x, p=0.5)
        
        x = self.conv_fr(x)
        x = self.deconv1(x)
        
        pool4 = self.conv_p4(pool4)
        pool4 = self.cropAs(pool4, x)
        
        fuse1 = torch.add(x, pool4)
        fuse1 = self.deconv2(fuse1)
        
        pool3 = self.conv_p3(pool3)
        pool3 = self.cropAs(pool3, fuse1)
        
        fuse2 = torch.add(fuse1, pool3)
        fuse2 = self.deconv3(fuse2)
        fuse2 = self.cropAs(fuse2, data)
        unary, q0 = fuse2.split(fuse2.shape[1]//2, dim=1)
        
        out = self.crf(unary, q0, data)
        
        return out
    


        
        
        
        
        