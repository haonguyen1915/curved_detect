from math import pi, cos, sin
import config
import cv2
import random


def waitKey(number):
    k = cv2.waitKey(number)
    if k == ord('q'): exit(0)
    return k


def imwrite(img, path):
    cv2.imwrite(path, img)


def draw_line(image, p1, p2, color=config.COLOR_BLUE, thickness=2):
    """
    Draw line in image
    :param image: numpy image
    :param p1: (x1, y1)
    :param p2: (x2, y2)
    :param color:
    :param thickness:
    :return:
    """
    image = cv2.line(image, p1, p2, color, thickness=thickness)
    return image


def draw_circle(image, center_p, radius, color=config.COLOR_BLUE, thickness=2):
    _color = tuple([int(x) for x in color])
    image = cv2.circle(image, center_p, radius, _color, thickness)
    return image


def draw_rectangle(image, box, color=config.COLOR_RED, line_type=2, points=False):
    """
    if points = False:
        box = (x, y, w, h)
    elif points = True
        box = (x1, y1, x2, y2)
    """
    if color is None:
        R = random.randint(0, 255)
        G = random.randint(0, 255)
        B = random.randint(0, 255)
        color = (R, G, B)
    if points:
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), color, line_type)
    else:
        cv2.rectangle(image, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), color, line_type)
    return image


def convert_rect_to_2p(box_rect):
    """
    Convert two Rect (x, y, w, h) to (x1, y1, x2, y2)
    :param box_rect: (x, y, w, h)
    :return: (x1, y1, x2, y2)
    """
    x, y, w, h = box_rect
    return (x, y, x + w, y + h)


def resize_image(img):
    scaling_factor = 1.0
    height, width = img.shape[:2]
    max_height = config.MAX_HEIGHT
    max_width = config.MAX_WIDTH
    if max_height == -1 or max_width == -1:
        return img, scaling_factor
    # only shrink if img is bigger than required
    if max_height < height or max_width < width:
        # get scaling factor
        scaling_factor = max_height / float(height)
        if max_width / float(width) < scaling_factor:
            scaling_factor = max_width / float(width)
        img = cv2.resize(img, None, fx=scaling_factor, fy=scaling_factor, interpolation=cv2.INTER_AREA)
    return img, scaling_factor


def filter_contour(contours):
    if len(contours) == 0:
        return []
    max_size = -1
    best_idx = -1
    filter_contours = []
    for idx, c in enumerate(contours):
        size = c.shape
        if size[0] > max_size:
            best_idx = idx
            max_size = size[0]
        if size[0] > 100:
            filter_contours.append(c)
    # return filter_contours
    return [contours[best_idx]]


def rotate_point(p1, center, angle):
    angle = pi * (angle - 90) / 180
    x1, y1 = p1
    x0, y0 = center
    a = angle
    x2 = ((x1 - x0) * cos(a)) - ((y1 - y0) * sin(a)) + x0
    y2 = ((x1 - x0) * sin(a)) + ((y1 - y0) * cos(a)) + y0
    return int(x2), int(y2)


def get_major_points(p1, p2, angle):
    i_p1 = int(p1[0]), int(p1[1])
    M1 = (i_p1[0], i_p1[1] - int(p2[1] / 2))
    major_p_1 = rotate_point(M1, p1, angle + 90)
    major_p_2 = rotate_point(M1, p1, angle + 90 + 180)
    major_points = (major_p_1, major_p_2)
    return major_points


def get_minor_points(p1, p2, angle):
    i_p1 = int(p1[0]), int(p1[1])
    i_p2 = int(p2[0]), int(p2[1])
    m1 = (i_p1[0], i_p1[1] - int(p2[0] / 2))
    minor_point_1 = rotate_point(m1, p1, angle)
    minor_point_2 = rotate_point(m1, p1, angle + 180)
    minor_points = (minor_point_1, minor_point_2)
    return minor_points


def check_a_point_within_rect(rect, p):
    """

    :param rect: x, y, w, h
    :param point:
    :return:
    """
    x1, y1, x2, y2 = convert_rect_to_2p(rect)
    return x1 < p[0] < x2 and y1 < p[1] < y2


def count_points_in_rect(rect, contours):
    """
    Count the countour in a box
    :param rect: (x, y, w, h)
    :param contours:
    :return:
    """
    assert len(contours) == 1

    counter = 0
    for p in contours[0]:
        # print(p)
        # print(p[0][0])
        # exit()
        # exit()
        if check_a_point_within_rect(rect, p[0]):
            counter += 1
    return counter


def get_center_point(contours, minor_points, image=None):
    first_rect = (
        minor_points[0][0] - config.MINOR_SQUARE_EXTEND,
        minor_points[0][1] - config.MINOR_SQUARE_EXTEND,
        config.MINOR_SQUARE_EXTEND * 2,
        config.MINOR_SQUARE_EXTEND * 2,
    )
    second_rect = (
        minor_points[1][0] - config.MINOR_SQUARE_EXTEND,
        minor_points[1][1] - config.MINOR_SQUARE_EXTEND,
        config.MINOR_SQUARE_EXTEND * 2,
        config.MINOR_SQUARE_EXTEND * 2,
    )
    first_num = count_points_in_rect(first_rect, contours)
    second_num = count_points_in_rect(second_rect, contours)
    hold_point = minor_points[0] if first_num >= second_num else minor_points[1]
    if config.DEBUG:
        print(f"number_1: {first_num}")
        print(f"number_2: {second_num}")
        rect = first_rect if first_num >= second_num else second_rect
        draw_rectangle(image, rect)
    return hold_point
