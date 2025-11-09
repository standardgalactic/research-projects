from scipy.optimize import minimize
from scipy.stats import entropy
def kld_objective(params,N,M,CD,lamR,L,pmf):
    import numpy as np
    pred=np.exp(pmf(N,M,params,CD,lamR,L))
    return entropy(N+M,pred+1e-12)
