"""OSNet appearance Re-ID."""


class ReID:
    def __init__(self, weights_path: str = "backend/models/weights/osnet.pth"):
        # TODO: load OSNet model
        self.weights_path = weights_path

    def extract_features(self, crop):
        """Returns a feature vector for the given player crop."""
        raise NotImplementedError
