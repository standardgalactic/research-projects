#!/usr/bin/env python3
"""faiss_index.py
Builds / updates a FAISS index from .vector files and exposes a simple search function.
"""
import faiss
import numpy as np
import os
from pathlib import Path
import pickle

INDEX_PATH = os.environ.get('FAISS_INDEX_PATH','to_process/faiss.index')
VEC_DIR = os.environ.get('VEC_DIR','to_process/memories')
META_PATH = os.environ.get('FAISS_META','to_process/faiss_meta.pkl')

def load_vectors(vec_dir):
    vec_dir = Path(vec_dir)
    vec_files = sorted(vec_dir.glob('*.vector'))
    ids=[]
    mats=[]
    for vf in vec_files:
        try:
            arr = np.load(vf)
            mats.append(arr.astype('float32'))
            ids.append(vf.with_suffix('.memory').name)
        except Exception as e:
            print('skipping', vf, e)
    if not mats:
        return [], None
    mat = np.stack(mats)
    return ids, mat

def build_index(vec_dir=VEC_DIR, index_path=INDEX_PATH, meta_path=META_PATH):
    ids, mat = load_vectors(vec_dir)
    if mat is None:
        print('No vectors found.')
        return
    d = mat.shape[1]
    index = faiss.IndexFlatIP(d)  # inner product (use normalized vectors)
    faiss.normalize_L2(mat)
    index.add(mat)
    faiss.write_index(index, index_path)
    with open(meta_path,'wb') as f:
        pickle.dump(ids, f)
    print('Built index with', index.ntotal, 'vectors')

def search(query_vec, k=10, index_path=INDEX_PATH, meta_path=META_PATH):
    if not os.path.exists(index_path):
        raise FileNotFoundError('Index not found')
    index = faiss.read_index(index_path)
    faiss.normalize_L2(query_vec)
    D,I = index.search(query_vec, k)
    with open(meta_path,'rb') as f:
        ids = pickle.load(f)
    results = []
    for row_i, row in enumerate(I):
        for rank,pos in enumerate(row):
            mem_id = ids[pos]
            results.append((mem_id, float(D[row_i, rank])))
    return results

if __name__ == '__main__':
    build_index()
