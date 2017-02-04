import numpy as np
import cv2
from markerfunctions import *
from markerdatabase import *

class Markers:
    
    QUADRILATERAL_POINTS = 4
    BLACK_THRESHOLD = 100
    WHITE_THRESHOLD = 155
    MARKER_NAME_INDEX = 3

    def __init__(self, debugOn=False):
        self.markerFound = False
        self.showDebug = debugOn
        with np.load('calibration/webcam_calibration_ouput.npz') as X:
            self.mtx, self.dist, _, _ = [X[i] for i in ('mtx','dist','rvecs','tvecs')]

    def setDebug(self, on_off):
        self.showDebug = on_off

    def detect(self, image):

        markers = []

        # Stage 1: Detect edges in image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if self.showDebug:
            cv2.imshow('Original gray', gray)
        gray = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(gray, 100, 175)  # 100, 200
        if self.showDebug:
            cv2.imshow('Blurred gray', gray)
            cv2.imshow('Edges detected', edges)

        # Stage 2: Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for i, contour in enumerate(contours):

            # Stage 3: Shape check
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.01*perimeter, True)

            if len(approx) == self.QUADRILATERAL_POINTS:

                # Stage 4: Perspective warping
                topdown_quad = get_topdown_quad(gray, approx.reshape(4, 2))

                if self.showDebug:
                    cv2.imshow('Quadrilaterals detected', topdown_quad)

                # Stage 5: Border check
                if topdown_quad[(topdown_quad.shape[0]/10.0),
                                (topdown_quad.shape[1]/10.0)] > self.BLACK_THRESHOLD: continue

                # Stage 6: Get marker pattern
                marker_pattern = None

                if self.showDebug:
                    cv2.drawContours(image, contours, i + 1, (255, 0, 0), 3)
                    cv2.imshow('contour', image)
                
                try:
                    marker_pattern = get_marker_pattern(topdown_quad, self.BLACK_THRESHOLD, self.WHITE_THRESHOLD)
                except:
                    continue
                
                if not marker_pattern: continue

                # Stage 7: Match marker pattern
                marker_found, marker_rotation, marker_name = match_marker_pattern(marker_pattern)
                self.markerFound = marker_found

                if marker_found:

                    # Stage 8: Duplicate marker check
                    if marker_name in [marker[self.MARKER_NAME_INDEX] for marker in markers]: continue

                    # Stage 9: Get rotation and translation vectors
                    rvecs, tvecs = get_vectors(image, approx.reshape(4, 2), self.mtx, self.dist)
                    markers.append([rvecs, tvecs, marker_rotation, marker_name, approx.reshape(4, 2)])

        return markers