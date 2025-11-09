import numpy as np
def noise_decomp(counts):
    arr=np.array(counts)
    return arr.var(), arr.mean()
