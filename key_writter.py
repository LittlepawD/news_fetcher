"""
Tool for pickling api keys, in format: news api key, bot api key, O_KEY.
Only run this if your api keys have changed or keys.bin is missing.
"""
import pickle

# keys are not real - see your own api tokens and insert here. 
keys = ("empty","empty","empty")

with open("keys.bin", "wb") as f:
    pickle.dump(keys, f)
