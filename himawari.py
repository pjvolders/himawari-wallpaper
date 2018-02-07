#!/usr/bin/env python3

# This is a very crude script. It could be better and user friendly, but
# it does what /I/ need it to do for now, so I didn't go the extra mile(s).

# It grabs the tiles used on http://himawari8.nict.go.jp/ to create an
# image that can be used as a wallpaper.
# The timestamp for the latest imaging available is taken from
#   http://himawari8.nict.go.jp/img/D531106/latest.json
# The corresponding tiles are available from
#   http://himawari8.nict.go.jp/img/D531106/<TILE_NUMBERS>d/550/<year>/<month>/<day>/<hh><mm><ss>_<x>_<y>.png
# where:
# - TILE_NUMBERS can be 2, 4, 8, 16 or 20. The bigger the number the more
#   detail in the tiles.
# - year, month, day, hh, mm, ss correspond to the timestamp
# - x and y are horizontal and vertical tile index, between 0 and
#   TILE_NUMBERS - 1.

# The adjustable parameters are:
# - HORIZONTAL: a range of tile numbers to use horizontally
# - VERTICAL: a range of tile numbers to use vertically
# - TIME_NUMBERS: see above.
# - SCALE: the size each tile is scaled to
# - IMAGE_PATH: the path where the aggregated image will be stored and updated.
# - TIME_OFFSET: by default, the latest picture will be grabbed. You can change this with this parameter

import os
import requests
import time
from datetime import datetime, timedelta
from PIL import Image, ImageOps, ImageEnhance, ImageMath
from subprocess import call
import math

# HORIZONTAL = tuple(range(0, 3))
# VERTICAL = tuple(range(0, 3))
TILE_NUMBERS = 2
HORIZONTAL = tuple(range(0, TILE_NUMBERS))
VERTICAL = tuple(range(0, TILE_NUMBERS))
SCALE = 550
IMAGE = 'D531106'
HIMAWARI = 'himawari8.nict.go.jp'
SLEEP_TIME = 60
TIMEOUT = 5
#TIME_OFFSET = timedelta()
TIME_OFFSET = timedelta(hours=-9, minutes=20)

IMAGE_PATH = 'Himawari.png'
IMAGE_TMP_PATH = '%s_%s' % os.path.splitext(IMAGE_PATH)
IMAGE_FOLDER = 'tmp_himawari/'

BASE_URL = 'http://%s/img/%s' % (HIMAWARI, IMAGE)

last_date = None

cur_dir = os.getcwd()

while True:
    session = requests.Session()
    try:
        response = session.get('%s/latest.json' % (BASE_URL), timeout=TIMEOUT)
        if response.status_code != 200:
            continue

        date_string = response.json().get('date')
        date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        date += TIME_OFFSET
    except:
        continue
    
    if date == last_date:
        time.sleep(SLEEP_TIME)
        continue

    # proceeding, getting new image for date
    print(date)
    image = Image.new('RGB', tuple(SCALE * len(n)
                                   for n in (HORIZONTAL, VERTICAL)))

    for x, h in enumerate(HORIZONTAL):
        for y, v in enumerate(VERTICAL):
            try:
                url = '%s/%dd/550/%s_%d_%d.png' % (BASE_URL, TILE_NUMBERS, date.strftime('%Y/%m/%d/%H%M%S'), h, v)
                print(url)
                response = session.get(url, stream=True, timeout=TIMEOUT)
                if response.status_code != 200:
                    continue
                tile = Image.open(response.raw)
            except:
                continue
            image.paste(tile.resize((SCALE, SCALE), Image.BILINEAR),
                        tuple(n * SCALE for n in (x, y)))

    new_image = ImageOps.expand(image, border=int(TILE_NUMBERS*SCALE*0.1))
    (new_image_r, new_image_g, new_image_b) = new_image.split()

    def gamma_1_2(c, gamma = 1.2):
        value = (c/255)**(1/gamma) * 255
        return max(0, min(255, value))
    def gamma_1_1(c, gamma = 1.1):
        value = (c/255)**(1/gamma) * 255
        return max(0, min(255, value))
    new_image_r = new_image_r.point(gamma_1_2)
    new_image_g = new_image_g.point(gamma_1_1)

    def contrast(u):
        c = 3 #contrast
        mp = .5 #mid-point
        u = u/255
        u = ( 1/(1+math.exp(c*(mp-u))) - 1/(1+math.exp(c*mp)) ) / ( 1/(1+math.exp(c*(mp-1))) - 1/(1+math.exp(c*mp)) )
        return u*255

    better_img = Image.merge('RGB', (new_image_r, new_image_g, new_image_b)).point(contrast)

    better_img.save(IMAGE_TMP_PATH)
    #os.rename(IMAGE_TMP_PATH, IMAGE_PATH)

    # hack for mac osx
    img_path = os.path.splitext(IMAGE_PATH)
    new_file = IMAGE_FOLDER+date.strftime('%Y_%m_%d_%H%M%S')+img_path[1]
    os.rename(IMAGE_TMP_PATH, new_file)

    osascript_line = "tell application \"Finder\" to set desktop picture to POSIX file \"%s/%s\"" % (cur_dir, new_file)
    osascript_line = "'"+osascript_line+"'"

    call("osascript -e "+osascript_line, shell=True)
    last_date = date
