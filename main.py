from utility import *
import config
import copy
import numpy as np


def process(image, contours, index=None):
    _image = copy.deepcopy(image)
    for c in contours:
        ellips = cv2.fitEllipse(c)
        print(ellips)
        cv2.ellipse(_image, ellips, (0, 255, 0), 2)
        p1, p2, angle = ellips
        minor_points = get_minor_points(p1, p2, angle)
        major_points = get_major_points(p1, p2, angle)

        holder_point = get_center_point(contours, minor_points, _image)
    if config.DEBUG:
        _image = draw_line(_image, p1=minor_points[0], p2=minor_points[1])
        _image = draw_line(_image, p1=major_points[0], p2=major_points[1], color=config.COLOR_MAGENTA)
        _image = draw_circle(_image, major_points[0], 4, thickness=2, color=config.COLOR_RED)
        _image = draw_circle(_image, major_points[1], 4, thickness=2, color=config.COLOR_RED)
        if index is not None:
            imwrite(_image, f"output/{str(index)}.jpg")

        cv2.imshow("_image", _image)
    return major_points, holder_point


def detect_object(image):
    height, width = image.shape[0], image.shape[1]
    kernel = np.ones((3, 3), np.uint8)
    image = cv2.dilate(image, kernel, iterations=3)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    inputImageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(inputImageGray, 150, 200, apertureSize=3)
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(contours)
    filtered_contours = filter_contour(contours)
    if config.DEBUG:
        print(f"size: {image.shape}")
        blank_image = np.zeros((height, width, 3), np.uint8)
        cv2.drawContours(blank_image, filtered_contours, -1, (0, 255, 0), 2)
        cv2.imshow("contours", blank_image)

    return filtered_contours, image


if __name__ == "__main__":
    for i in range(1, 8):
        origin_image = cv2.imread(f"data/{str(i)}.jpg")
        inputImage, scaling_factor = resize_image(origin_image)
        output_contours, outputImage = detect_object(inputImage)
        major_points, holder_point = process(outputImage, output_contours, i)

        if config.DEBUG:
            holder_p = int(holder_point[0] * (1.0 / scaling_factor)), int(holder_point[1] * (1.0 / scaling_factor))
            print(f"scale factor: {scaling_factor}")
            origin_image = draw_circle(origin_image, center_p=holder_p, radius=10)
            cv2.imshow("origin image", origin_image)
            waitKey(0)
