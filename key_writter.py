"""
Tool for pickling api keys, in format: N_KEY, M_KEY, O_KEY.
"""

keys = ("empty","empty","empty")
import pickle

with open("keys.bin", "wb") as f:
    pickle.dump(keys, f)
