import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from reid import ReID
from scipy.spatial.distance import cosine

reid = ReID()

# pretend we have two player crops (just random noise images for testing)
fake_crop_1 = np.random.randint(0, 255, (256, 128, 3), dtype=np.uint8)
fake_crop_2 = np.random.randint(0, 255, (256, 128, 3), dtype=np.uint8)

# extract embeddings
emb1 = reid.extract_features(fake_crop_1)
emb2 = reid.extract_features(fake_crop_2)

print("Embedding shape:", emb1.shape)    # should print (512,)
print("Embedding norm:", np.linalg.norm(emb1))   # should print ~1.0

# test gallery
reid.update_gallery(tracker_id=1, embedding=emb1)
match = reid.match(emb1)   # should match tracker_id 1
print("Match for emb1:", match)   # should print 1

match2 = reid.match(emb2)  # random crop, probably no match
print("Match for emb2:", match2)  # likely None

sim = 1 - cosine(emb1, emb2)
print("Similarity between two random crops:", sim)