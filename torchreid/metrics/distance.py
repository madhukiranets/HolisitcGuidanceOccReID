from __future__ import division, print_function, absolute_import
import torch
from torch.nn import functional as F


def compute_weight_distance_matrix(input1, input2, input1_score, input2_score, metric='euclidean'):
    
    """A wrapper function for computing distance matrix.
    Args:
        input1 (torch.Tensor): 3-D feature matrix. N1*C*P
        input2 (torch.Tensor): 3-D feature matrix. N2*C*P
        input1_score N1*P
        input2_score N2*P
        metric (str, optional): "euclidean" or "cosine".
            Default is "euclidean".
    Returns:
        torch.Tensor: distance matrix.
    Examples::
       >>> from torchreid import metrics
       >>> input1 = torch.rand(10, 2048)
       >>> input2 = torch.rand(100, 2048)
       >>> distmat = metrics.compute_distance_matrix(input1, input2)
       >>> distmat.size() # (10, 100)
    """
    # check input

    input1_score = input1_score.unsqueeze(1).expand(input1.size(0),input2.size(0),input1.size(2))
    input2_score = input2_score.unsqueeze(0).expand(input1.size(0),input2.size(0),input1.size(2))
    score_map = input1_score*input2_score
    distmat = 0
    for i in range(input1.size(2)):
        if metric == 'euclidean':
            distmat += score_map[:,:,i]*euclidean_squared_distance(input1[:,:,i], input2[:,:,i])
        elif metric == 'cosine':
            distmat += score_map[:,:,i]*cosine_distance(input1[:,:,i], input2[:,:,i])
        else:
            raise ValueError(
                'Unknown distance metric: {}. '
                'Please choose either "euclidean" or "cosine"'.format(metric)
            )
    distmat = distmat/(score_map.sum(2))

    return distmat

def compute_weight_distance_matrix_NOMASK(input1, input2, metric='euclidean'):
    
    """A wrapper function for computing distance matrix.
    Args:
        input1 (torch.Tensor): 3-D feature matrix. N1*C*P
        input2 (torch.Tensor): 3-D feature matrix. N2*C*P
        input1_score N1*P
        input2_score N2*P
        metric (str, optional): "euclidean" or "cosine".
            Default is "euclidean".
    Returns:
        torch.Tensor: distance matrix.
    Examples::
       >>> from torchreid import metrics
       >>> input1 = torch.rand(10, 2048)
       >>> input2 = torch.rand(100, 2048)
       >>> distmat = metrics.compute_distance_matrix(input1, input2)
       >>> distmat.size() # (10, 100)
    """
    # check input
    metric='euclidean'
    distmat = 0
    i=0
    for i in range(input1.size(2)):
       
        if metric == 'euclidean':
            
            distmat += euclidean_squared_distance(input1[:,:,i], input2[:,:,i])
        elif metric == 'cosine':
            distmat += cosine_distance(input1[:,:,i], input2[:,:,i])
        else:
            raise ValueError(
                'Unknown distance metric: {}. '
                'Please choose either "euclidean" or "cosine"'.format(metric)
            )
    distmat = distmat

    return distmat

def compute_distance_matrix(input1, input2, metric='euclidean'):
    """A wrapper function for computing distance matrix.

    Args:
        input1 (torch.Tensor): 2-D feature matrix.
        input2 (torch.Tensor): 2-D feature matrix.
        metric (str, optional): "euclidean" or "cosine".
            Default is "euclidean".

    Returns:
        torch.Tensor: distance matrix.

    Examples::
       >>> from torchreid import metrics
       >>> input1 = torch.rand(10, 2048)
       >>> input2 = torch.rand(100, 2048)
       >>> distmat = metrics.compute_distance_matrix(input1, input2)
       >>> distmat.size() # (10, 100)
    """
    # check input
    
    assert isinstance(input1, torch.Tensor)
    assert isinstance(input2, torch.Tensor)
    assert input1.dim() == 2, 'Expected 2-D tensor, but got {}-D'.format(
        input1.dim()
    )
    assert input2.dim() == 2, 'Expected 2-D tensor, but got {}-D'.format(
        input2.dim()
    )
    assert input1.size(1) == input2.size(1)

    if metric == 'euclidean':
        distmat = euclidean_squared_distance(input1, input2)
    elif metric == 'cosine':
        distmat = cosine_distance(input1, input2)
    else:
        raise ValueError(
            'Unknown distance metric: {}. '
            'Please choose either "euclidean" or "cosine"'.format(metric)
        )

    return distmat


def euclidean_squared_distance(input1, input2):
    """Computes euclidean squared distance.

    Args:
        input1 (torch.Tensor): 2-D feature matrix.
        input2 (torch.Tensor): 2-D feature matrix.

    Returns:
        torch.Tensor: distance matrix.
    """
    m, n = input1.size(0), input2.size(0)
    distmat = torch.pow(input1, 2).sum(dim=1, keepdim=True).expand(m, n) + \
              torch.pow(input2, 2).sum(dim=1, keepdim=True).expand(n, m).t()
    distmat.addmm_(1, -2, input1, input2.t())
    return distmat


def cosine_distance(input1, input2):
    """Computes cosine distance.

    Args:
        input1 (torch.Tensor): 2-D feature matrix.
        input2 (torch.Tensor): 2-D feature matrix.

    Returns:
        torch.Tensor: distance matrix.
    """
    input1_normed = F.normalize(input1, p=2, dim=1)
    input2_normed = F.normalize(input2, p=2, dim=1)
    distmat = 1 - torch.mm(input1_normed, input2_normed.t())
    return distmat
