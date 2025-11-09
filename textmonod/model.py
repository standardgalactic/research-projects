import numpy as np
from scipy.stats import poisson, nbinom, gamma

def constitutive_pmf(n, mu):
    return poisson.pmf(n, mu)

def bursty_pmf(n, p, r):
    return nbinom.pmf(n, r, p)

def extrinsic_rate_sample(theta, kshape):
    return gamma.rvs(kshape, scale=theta)