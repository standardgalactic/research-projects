from textmonod.utils import token_diff
from textmonod.inference import kld_objective
v0=["a","b"]; v1=["a","b","c"]
N,M,L=token_diff(v0,v1)
print("Diff:",N,M,L)
