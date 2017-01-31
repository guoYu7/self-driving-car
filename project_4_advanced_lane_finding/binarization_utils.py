import cv2
import numpy as np
import glob
import matplotlib.pyplot as plt
import os.path as path
import pickle


white_HSV_th_min = np.array([0, 0, 210])
white_HSV_th_max = np.array([255, 255, 255])

yellow_HSV_th_min = np.array([0, 80, 210])
yellow_HSV_th_max = np.array([30, 255, 255])


def thresh_frame_in_HSV(frame, min_values, max_values, verbose=False):

    HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    min_th_ok = np.all(HSV > min_values, axis=2)
    max_th_ok = np.all(HSV < max_values, axis=2)

    out = np.logical_and(min_th_ok, max_th_ok)

    if verbose:
        plt.imshow(out, cmap='gray')
        plt.show()

    return out


def thresh_frame_sobel(frame, kernel_size):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel_size)

    sobel_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    sobel_mag = np.uint8(sobel_mag / np.max(sobel_mag) * 255)

    _, sobel_mag = cv2.threshold(sobel_mag, 128, 1, cv2.THRESH_BINARY)

    return sobel_mag.astype(bool)


def binarize(img, verbose=False):

    subsample = 2
    h, w = img.shape[:2]

    img = cv2.resize(img, dsize=(w // subsample, h // subsample))

    white_binary = thresh_frame_in_HSV(img, white_HSV_th_min, white_HSV_th_max)
    yellow_binary = thresh_frame_in_HSV(img, yellow_HSV_th_min, yellow_HSV_th_max)

    mask_HSV = np.logical_or(white_binary, yellow_binary)

    mask_sobel = thresh_frame_sobel(img, kernel_size=9)

    binary = np.logical_or(mask_HSV, mask_sobel)

    kernel = np.ones((7, 7), np.uint8)
    closing = cv2.morphologyEx(binary.astype(np.uint8), cv2.MORPH_CLOSE, kernel)

    if verbose:
        f, ax = plt.subplots(2, 2)
        ax[0, 0].imshow(white_binary, cmap='gray')
        ax[0, 0].set_title('white binary')
        ax[0, 0].set_axis_off()
        ax[0, 1].imshow(yellow_binary, cmap='gray')
        ax[0, 1].set_title('yellow binary')
        ax[0, 1].set_axis_off()
        ax[1, 0].imshow(binary, cmap='gray')
        ax[1, 0].set_title('before close')
        ax[1, 0].set_axis_off()
        ax[1, 1].imshow(closing, cmap='gray')
        ax[1, 1].set_title('after close')
        ax[1, 1].set_axis_off()
        plt.show()

    return img


if __name__ == '__main__':

    test_images = glob.glob('test_images/*.jpg')
    for test_image in test_images:
        img = cv2.imread(test_image)

        binarize(img=img, verbose=True)