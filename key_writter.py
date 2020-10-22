"""
Warning! Do not add this to commits anymore!!

Tool for pickling api keys, in format: news api key, bot api key, O_KEY.
"""
import pickle

# keys are not real - see your own api tokens and insert here. 
keys = ("da1e5458baf040e99e8fb951a978a719","820678802:AAF-Yre6EK5Jyjeqi9EYjMmsd2WS1nr2TiY","empty")

with open("keys.bin", "wb") as f:
    pickle.dump(keys, f)
