import numpy as np

def variance_decompose(trajs):
    session_var=[np.var(v,ddof=1) for v in trajs]
    within=np.mean(session_var)
    means=[np.mean(v) for v in trajs]
    between=np.var(means,ddof=1)
    return {'within':within,'between':between,'total':within+between}