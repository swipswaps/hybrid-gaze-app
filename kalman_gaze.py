# Discrete Kalman Filter implementation for gaze coordinate stabilization
# Reference: Kalman, R. E. (1960). "A New Approach to Linear Filtering and Prediction Problems." Journal of Basic Engineering, 82(1), 35–45. DOI: 10.1115/1.3662552.

import cv2
import numpy as np

class GazeKalmanTracker:
    def __init__(self):
        # 4-state vector [x, y, dx, dy] and 2-measurement vector [x, y]
        self.kf = cv2.KalmanFilter(4, 2)
        self.kf.measurementMatrix = np.array([[1, 0, 0, 0],
                                              [0, 1, 0, 0]], np.float32)
        self.kf.transitionMatrix = np.array([[1, 0, 1, 0],
                                             [0, 1, 0, 1],
                                             [0, 0, 1, 0],
                                             [0, 0, 0, 1]], np.float32)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.03
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.5

    def filter_point(self, x: float, y: float):
        measured = np.array([[np.float32(x)], [np.float32(y)]])
        self.kf.correct(measured)
        predicted = self.kf.predict()
        return float(predicted[0]), float(predicted[1])
