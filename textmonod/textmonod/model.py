from scipy.stats import nbinom, poisson
def bursty_pmf(N,M,params,CD,lamR,L):
    r,p=params.get('b_size',2),params.get('b_rate',0.5)
    return nbinom.logpmf(N,r,p) + poisson.logpmf(M, lamR*(params.get('beta',1)/params.get('gamma',1)))
