"""
Tool for pickling api keys, in format: N_KEY, M_KEY, O_KEY.
"""
import pickle

keys = ("empty","empty","empty")

with open("keys.bin", "wb") as f:
    pickle.dump(keys, f)
