import numpy as np
from scipy.optimize import minimize
from .model import constitutive_pmf, bursty_pmf

def kl_div(p,q,eps=1e-12):
    p=np.array(p); q=np.array(q)+eps
    return np.sum(p*np.log((p+eps)/q))

def fit_constitutive(emp_counts):
    hist,_=np.histogram(emp_counts,bins=50,density=True)
    x=np.arange(len(hist))
    def obj(mu):
        q=[constitutive_pmf(i,mu) for i in x]
        return kl_div(hist,q)
    res=minimize(lambda m:obj(m[0]),x0=[np.mean(emp_counts)],bounds=[(1e-3,None)])
    return res.x[0]

def grid_search_tech(loss_fn,grid1,grid2):
    best=(None,float('inf'))
    for a in grid1:
        for b in grid2:
            l=loss_fn(a,b)
            if l<best[1]: best=((a,b),l)
    return best

def fisher_information(loglik,theta,eps=1e-3):
    n=len(theta); F=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            d=theta.copy()
            d[i]+=eps; d2=theta.copy(); d2[j]+=eps
            F[i,j]=(loglik(d)+loglik(d2)-2*loglik(theta))/(eps**2)
    return F