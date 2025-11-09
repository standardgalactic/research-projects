import numpy as np
from textmonod.model import constitutive_pmf
from textmonod.inference import fit_constitutive, fisher_information
from textmonod.decomposition import variance_decompose

np.random.seed(0)
true_mu=5
samples=np.random.poisson(true_mu,200)
mu_hat=fit_constitutive(samples)
print('Fitted mu:',mu_hat)

def ll(theta):
    mu=theta[0]; return np.sum(np.log(constitutive_pmf(samples,mu)+1e-12))
F=fisher_information(ll,[mu_hat])
print('FIM approx:',F)

trajs=[np.random.poisson(true_mu,50) for _ in range(5)]
print('Var parts:',variance_decompose(trajs))