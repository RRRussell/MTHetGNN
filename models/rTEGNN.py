import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
#from layers import GraphAttentionLayer, SpGraphAttentionLayer
from layer import DeGINConv,DenseGCNConv,DenseSAGEConv,DenseGraphConv,rkGraphConv,graph_constructor
#from torch_geometric.nn import GATConv

class Model(nn.Module):

    def __init__(self, args,data):
        super(Model,self).__init__()
        self.use_cuda = args.cuda
        A = np.loadtxt(args.A)
        A = np.array(A,dtype=np.float32)
        A[A>0.05] = 1
        A = A/np.sum(A,0)
        A_new = np.zeros((args.batch_size,args.n_e,args.n_e),dtype=np.float32)
        for i in range(args.batch_size):
            A_new[i,:,:]=A

        # Transfer Entropy matrix
        self.A = torch.from_numpy(A_new).cuda()
        self.adjs = [self.A]
        self.num_adjs = args.num_adj

        if self.num_adjs>1:
            B = np.loadtxt(args.B)
            B = np.array(B, dtype=np.float32)

            B[B>0.05] = 1
            B = B / np.sum(B, 0)
            B_new = np.zeros((args.batch_size, args.n_e, args.n_e), dtype=np.float32)
            for i in range(args.batch_size):
                B_new[i, :, :] = B

            # Correlation Coefficient Matrix
            self.B = torch.from_numpy(B_new).cuda()

            self.adjs = [self.A,self.B,self.B]

        subgraph_size = args.subgraph_size
        node_dim = 40
        self.device = torch.device(args.device)
        tanhalpha = 3
        self.gc = graph_constructor(args.n_e, subgraph_size, node_dim, self.device, alpha=tanhalpha,
                                    static_feat=None)
        self.n_e=args.n_e
        self.decoder = args.decoder
        self.attention_mode = args.attention_mode

        # if self.decoder != 'GAT':
        ##The hyper-parameters are applied to all datasets in all horizons
        self.conv1=nn.Conv2d(1, args.channel_size, kernel_size = (1,args.k_size[0]),stride=1)
        self.conv2=nn.Conv2d(1, args.channel_size, kernel_size = (1,args.k_size[1]),stride=1)
        self.conv3=nn.Conv2d(1, args.channel_size, kernel_size = (1,args.k_size[2]),stride=1)

        d= (len(args.k_size)*(args.window) -sum(args.k_size)+ len(args.k_size))*args.channel_size
        skip_mode = args.skip_mode
        self.BATCH_SIZE=args.batch_size
        self.bn = nn.BatchNorm2d(1,affine = True)
        self.bn2 = nn.BatchNorm2d(1,affine= True)
        self.dropout = 0.1

        if self.decoder == 'GCN':
            self.gcn1 = DenseGCNConv(d, args.hid1)
            self.gcn2 = DenseGCNConv(args.hid1, args.hid2)
            self.gcn3 = DenseGCNConv(args.hid2, 1)

        if self.decoder == 'GNN':
            self.gnn1 = DenseGraphConv(d, args.hid1)
            self.gnn2 = DenseGraphConv(args.hid1, args.hid2)
            self.gnn3 = DenseGraphConv(args.hid2, 1)

        if self.decoder == 'rGNN':
            # self.num_adjs = 1
            self.gc1 = rkGraphConv(self.num_adjs,d,args.hid1,self.attention_mode,aggr='mean')
            self.gc2 = rkGraphConv(self.num_adjs,args.hid1,args.hid2,self.attention_mode,aggr='mean')
            self.gc3 = rkGraphConv(self.num_adjs,args.hid2, 1, self.attention_mode, aggr='mean')

        self.hw = args.highway_window
        if (self.hw > 0):
            self.highway = nn.Linear(self.hw, 1)

        if self.decoder == 'SAGE':
            self.sage1 = DenseSAGEConv(d,args.hid1)
            self.sage2 = DenseSAGEConv(args.hid1, args.hid2)
            self.sage3 = DenseSAGEConv(args.hid2, 1)

        if self.decoder == 'GIN':
            ginnn = nn.Sequential(
                nn.Linear(d,args.hid1),
                nn.ReLU(True),
                nn.Linear(args.hid1,1),
                nn.ReLU(True)
            )
            self.gin = DeGINConv(ginnn)
        if self.decoder == 'GAT':
            self.gatconv1 = GATConv(d,args.hid1)
            self.gatconv2 = GATConv(args.hid1,args.hid2)
            self.gatconv3 = GATConv(args.hid2,1)

    def skip_connect_out(self, x2, x1):
        return self.ff(torch.cat((x2, x1), 1)) if self.skip_mode=="concat" else x2+x1
    def forward(self,x):
        c=x.permute(0,2,1)
        c=c.unsqueeze(1)

        a1=self.conv1(c).permute(0,2,1,3).reshape(self.BATCH_SIZE,self.n_e,-1)
        a2=self.conv2(c).permute(0,2,1,3).reshape(self.BATCH_SIZE,self.n_e,-1)
        a3=self.conv3(c).permute(0,2,1,3).reshape(self.BATCH_SIZE,self.n_e,-1)
        x_conv = F.relu(torch.cat([a1, a2, a3], 2))

        # Dynamic Graph Adjacency matrix
        idx = [0]
        for i in range(1, self.n_e):
            idx.append(i)
        idx = torch.tensor(idx).to(self.device)
        adp = self.gc(idx,x)
        g = F.normalize(adp,p=1,dim=1)

        if self.decoder == 'GCN':
            # x1 = F.relu(self.gcn1(x_conv,self.A))
            x1 = F.relu(self.gcn1(x_conv, self.A))
            x2 = F.relu(self.gcn2(x1,self.A))
            x3 = self.gcn3(x2,self.A)
            x3 = x3.squeeze()

        if self.decoder == 'GNN':
        # x0 = F.relu(self.gnn0(x_conv,self.A))
            x1 = F.relu(self.gnn1(x_conv,self.A))
            x2 = F.relu(self.gnn2(x1,self.A))
            x3 = self.gnn3(x2,self.A)
            x3 = x3.squeeze()
        if self.decoder == 'rGNN':
            # Substitute All-one matrix
            if self.num_adjs == 3:
                self.adjs[2] = g
            x1 = F.relu(self.gc1(x_conv,self.adjs))
            x2 = F.relu(self.gc2(x1, self.adjs))
            x3 = self.gc3(x2, self.adjs)
            x3 = x3.squeeze()


        if self.decoder == 'SAGE':
            x1 = F.relu(self.sage1(x_conv,self.A))
            x2 = F.relu(self.sage2(x1,self.A))
            x3 = F.relu(self.sage3(x2,self.A))
            x3 = x3.squeeze()

        if self.decoder == 'GIN':
            x3 = F.relu(self.gin(x_conv, self.A))
            x3 = x3.squeeze()

        if self.decoder == 'GAT':
            x1 = F.relu(self.gatconv1(x_conv,self.edge_index))
            x2 = F.relu(self.gatconv2(x1,self.edge_index))
            x3 = F.relu(self.gatconv3(x2,self.edge_index))
            x3 = x3.squeeze()

        if self.hw>0:
            z = x[:, -self.hw:, :]
            z = z.permute(0, 2, 1)
            z = self.highway(z)
            z = z.squeeze(2)
            x3 = x3 + z
        return x3
