import random
import numpy as np

num =15000000


bits = bin(random.getrandbits(num))[2:].zfill(num)

with open("trad2", "w") as f:
    f.write(bits)
