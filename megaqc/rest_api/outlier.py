from numpy import absolute, delete, take, zeros
from outliers import smirnov_grubbs as grubbs
from scipy.stats import zscore


class OutlierDetector:
    def __init__(self, threshold=None):
        self.threshold = threshold

    def get_outliers(self, y):
        """
        Returns a boolean "mask array" that can be used to select outliers.
        """

        # This default implementation returns an array of 0s
        return zeros(len(y), dtype=bool)


class GrubbsDetector(OutlierDetector):
    def get_outliers(self, y):
        outlier_indices = grubbs.two_sided_test_indices(y, alpha=self.threshold)
        mask = zeros(len(y), dtype=bool)
        mask[outlier_indices] = 1
        return mask


class ZScoreDetector(OutlierDetector):
    def get_outliers(self, y):
        return absolute(zscore(y)) > self.threshold
