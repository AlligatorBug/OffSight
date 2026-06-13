# reid.py: identify players by face!
# player's appearance -> embedding vector
# same player  →  similar vectors  (close together)
# different player  →  different vectors  (far apart)
# OSNet (Omni-Scale Network) -> neural network specifically trained for person Re-ID -> available in torchreid library installed
# image → [a bunch of numbers] → embedding

import cv2
import torch
import torchreid
import numpy as np
from scipy.spatial.distance import cosine

class ReID:
    def __init__(self, weights_path: str = "backend/models/weights/osnet.pth"):
        self.model = torchreid.models.build_model(
            name="osnet_x1_0",
            num_classes=1000, # pretrained on 1000 person identities
            pretrained=True # download pretrained weights automatically
        )
        # set to evaluation mode — important!
        # tells PyTorch we're doing inference, not training
        # disables dropout and batch norm behaves differently in train vs eval
        self.model.eval()
        self.device = torch.device("cpu")
        self.model = self.model.to(self.device)
        
        # gallery stores embeddings of players we've already identified
        # { tracker_id: embedding_vector }
        self.gallery = {}
    
    def preprocess(self, crop): # crop is an OpenCV numpy array
        """Prepares a player crop for OSNet, OSNet expects: RGB, resized to 256x128, normalized"""
        # convert BGR -> RGB
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

        # resize to 256x128
        crop = cv2.resize(crop, (128, 256))

        # scale pixels from 0-255 → 0.0-1.0
        crop = crop.astype(np.float32) / 255.0

        # normalise using ImageNet mean and stdev
        mean = np.array([0.485, 0.456, 0.406])
        std  = np.array([0.229, 0.224, 0.225])
        crop = (crop - mean) / std

        # rearrange from (256, 128, 3) → (3, 256, 128)
        crop = crop.transpose(2, 0, 1)

        # add batch dimension: (3, 256, 128) → (1, 3, 256, 128)
        crop = np.expand_dims(crop, axis=0)

        # convert to pytorch tensor
        return torch.tensor(crop, dtype=torch.float32).to(self.device)

    def extract_features(self, crop):
        """
        Passes a player crop through OSNet to get an embedding vector.
        This embedding represents what the player looks like.

        Args:
            crop: BGR numpy array of a player bounding box

        Returns:
            embedding: 1D numpy array of shape [512]
                    represents the player's appearance
        """
        # guard against empty crops
        # (can happen if a player is right at the edge of the frame)
        if crop is None or crop.size == 0:
            return None
        
        # preprocess the crop into a tensor OSNet can accept
        tensor = self.preprocess(crop)

        # torch.no_grad() tells PyTorch not to compute gradients
        # we're doing inference not training so we don't need them
        # also saves memory and runs faster
        with torch.no_grad():
            embedding = self.model(tensor)
        
        # embedding comes out as shape [1, 512]
        # squeeze removes the batch dimension → [512]
        embedding = embedding.squeeze().numpy()

        # normalize the embedding vector to unit length
        # this makes cosine similarity more reliable
        # all vectors point the same "distance" from origin
        # only the direction matters — direction = identity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def update_gallery(self, tracker_id, embedding):
        """
        Stores a player's embedding in the gallery.
        Called whenever OCR successfully identifies a player —
        so we build up a reference of what each known player looks like.

        Args:
            tracker_id: ByteTrack ID for this player
            embedding:  Their appearance embedding from extract_features()
        """
        if embedding is not None:
            self.gallery[tracker_id] = embedding
    
    def match(self, embedding, threshold=0.85):
        """
        Compares an unknown player's embedding against the gallery
        to find who they most likely are.

        Args:
            embedding:  The unknown player's embedding vector
            threshold:  Minimum similarity to count as a match (0-1)
                        0.7 means "must be 70% similar to count"

        Returns:
            tracker_id of the best match, or None if no match found
        """
        if embedding is None or len(self.gallery) == 0:
            return None
        
        best_match_id = None
        best_similarity = 0

        for key, value in self.gallery.items():
            similarity = 1 - cosine(embedding, value)
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = key
        
        if best_similarity >= threshold:
            return best_match_id
        else:
            return None



