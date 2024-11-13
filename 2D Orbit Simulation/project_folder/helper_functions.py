
from mass import *
import random 
def pygame_array(list1, list2, WIDTH, HEIGHT):
    scaled_coordinates = [] 
    for n in range(len(list1)):
        x = 0.5*WIDTH*list1[n] + 0.5*WIDTH   # +/- x shift
        y = -0.5*WIDTH*list2[n] + 0.5*HEIGHT # +/- y shift
        scaled_coordinates.append((x, y))
    return scaled_coordinates

def translate_points_on_screen(pts=(0, 0), WIDTH=1, HEIGHT=1, screen_scale=1):
    position = []
    x = pts[0]/(0.5*WIDTH) -1
    y = (pts[1]-0.5*HEIGHT)/(0.5*WIDTH)
    position = [x*screen_scale, -y*screen_scale]
    return position

