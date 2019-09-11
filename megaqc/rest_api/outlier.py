from numpy import delete, take, absolute
from outliers import smirnov_grubbs as grubbs
from scipy.stats import zscore


class OutlierDetector:
    def __init__(self, threshold=None):
        self.threshold = threshold

    def split(self, x, y):
        """
        Split some x/y pairs using the threshold
        """

        # This default implementation returns the values as-is
        return x, [], y, []


class GrubbsDetector(OutlierDetector):

    def split(self, x, y):
        outliers = grubbs.two_sided_test_indices(y, alpha=self.threshold)
        x_outler, y_outlier = take(x, outliers), take(y, outliers)
        x_inlier, y_inlier = delete(x, outliers), delete(y, outliers)

        return x_inlier, x_outler, y_inlier, y_outlier


class ZScoreDetector(OutlierDetector):

    def split(self, x, y):
        outliers = absolute(zscore(y)) > self.threshold

        x_outler, y_outlier = x[outliers], y[outliers]
        x_inlier, y_inlier = x[~outliers], y[~outliers]

        return x_inlier, x_outler, y_inlier, y_outlier
