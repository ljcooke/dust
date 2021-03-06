#!/usr/bin/env python3
"""
SVG cosmic dust generator.

"""
import base64
import os
import subprocess
import sys
from random import choice, randint, random

import twitter
from mako.template import Template


__license__ = 'http://unlicense.org/'


TEMPLATE_PATH = 'template.svg'

OUTPUT_SVG_PATH = 'output.svg'
OUTPUT_PNG_PATH = 'output.png'
OUTPUT_CROP_PNG_PATH = 'output-crop.png'
OUTPUT_JPG_PATH = 'output-crop.jpg'
OUTPUT_JPG_QUALITY = 95

CANVAS_SIZE = (1880, 1400)
CROP_SIZE = (1680, 1200)

INT_MAX = 2 ** 64 - 1

DARK_VALUES = (0x11, 0x22, 0x33, 0x44, 0x55, 0x66)
MIDDLE_VALUES = (0x66, 0x77, 0x77, 0x88, 0x88, 0x99, 0x99, 0xAA)
BRIGHT_VALUES = (0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF)

EMOJI = """👽🌌✨🚀🌕🌑"""


def biased_randint(bias, upper):
    r_num = random() * random()
    if randint(0, 1) == 0:
        r_num *= random()
    return int(r_num * upper + bias) % (upper + 1)

def dust_svg(width, height, template_path=TEMPLATE_PATH):
    """
    Generate a dust image as SVG.

    """
    bias_x, bias_y = randint(0, width), randint(0, height)
    shadow_x, shadow_y = randint(0, width), randint(0, height)

    byteval = lambda n: min(max(0, int(n)), 255)

    rand_value_bright = lambda: (choice(BRIGHT_VALUES + (None,))
                                 or choice(DARK_VALUES))

    rand_value_middle = lambda: (choice(MIDDLE_VALUES + (None,))
                                 or choice(DARK_VALUES))

    rgb_bright = lambda: (rand_value_bright(),
                          rand_value_bright(),
                          rand_value_bright())
    rgb_middle = lambda: (rand_value_middle(),
                          rand_value_middle(),
                          rand_value_middle())
    rgb_redder  = lambda: (0xEE, rand_value_middle(), rand_value_middle())
    rgb_greener = lambda: (rand_value_middle(), 0xEE, rand_value_middle())
    rgb_bluer   = lambda: (rand_value_middle(), rand_value_middle(), 0xEE)

    rgb_focus = choice((
        (0xFF, 0x33, 0x33), (0xFF, 0x33, 0x33),
        (0x33, 0xFF, 0x33),
        (0x33, 0x33, 0xFF), (0x33, 0x33, 0xFF),
        (0xFF, 0x88, 0x33),
        (0x33, 0x88, 0xFF),
        (0xFF, 0x33, 0xFF),
    ))

    print('Width     : %d' % width)
    print('Height    : %d' % height)
    print('Gravity X : %d' % bias_x)
    print('Gravity Y : %d' % bias_y)
    print('Shadow X  : %d' % shadow_x)
    print('Shadow Y  : %d' % shadow_y)
    print('Color     : %s' % repr(rgb_focus))

    params = {
        'width': width,
        'height': height,
        'rand_x': lambda: randint(0, width),
        'rand_y': lambda: randint(0, height),
        'rand_bias_x': lambda: biased_randint(bias_x, width),
        'rand_bias_y': lambda: biased_randint(bias_y, height),
        'rand_shadow_x': lambda: biased_randint(shadow_x, width),
        'rand_shadow_y': lambda: biased_randint(shadow_y, height),

        'noise_base_freq': '%0.3f' % (random() * 0.1),
        'noise_seed': randint(0, INT_MAX),
        'noise_type': choice(('turbulence', 'fractalNoise')),

        'cloud_blur_amount': 35,
        'rand_cloud_alpha': '%0.3f' % ((random() * 0.04) + 0.1),
        'rand_cloud_bright_alpha': '%0.3f' % ((random() * 0.1) + 0.1),
        'rand_cloud_dark_alpha': '%0.3f' % ((random() * 0.2) + 0.1),
        'rand_cloud_radius': lambda: randint(200, 800),
        'rand_cloud_smaller_radius': lambda: randint(100, 400),
        'rand_cloud_rgb': lambda: '%d, %d, %d' % choice((
            rgb_bright, rgb_bright, rgb_bright, rgb_bright, rgb_bright,
            rgb_middle, rgb_middle,
            rgb_redder, rgb_redder, rgb_redder, rgb_redder, rgb_redder,
            rgb_greener,
            rgb_bluer, rgb_bluer, rgb_bluer, rgb_bluer, rgb_bluer,
            lambda: rgb_focus, lambda: rgb_focus,
        ))(),
        'rand_cloud_bright_rgb': lambda: '%d, %d, %d' % choice((
            (0xFF, 0xFF, 0xFF), (0xFF, 0xFF, 0xFF), (0xFF, 0xFF, 0xFF),
            rgb_focus,
        )),
        'rand_cloud_dark_rgb': lambda: '0, 0, 0',

        'star_blur_amount': 0.1,
        'rand_star_alpha': lambda: (
            choice((0.1, 0.1, 0.1, 0.2, 0.2))
            or '%.2f' % (random() * 0.5)
        ),
        'rand_star_offset': lambda: '%.2f' % (random() * random() * 2),
        'rand_star_radius': lambda: '%.2f' % (random() * random() * 0.5 + 0.25),
        'rand_star_rgb': lambda: '%d, %d, %d' % (
            byteval(rand_value_bright() * 1.25),
            byteval(rand_value_bright() * 1.25),
            byteval(rand_value_bright() * 1.25),
        ),
        'rand_star_type': lambda: choice((
            'star-bright',
            'star-bright',
            'star-bright',
            'star-faint',
            'star-faint',
            'star-faint',
            'star-faint',
            'star-faint',
            'star-red',
            'star-blue',
        )),
    }

    template = Template(filename=template_path)
    return template.render(**params)


def post_tweet(text, image_path=None,
               user_token=None, user_secret=None,
               consumer_key=None, consumer_secret=None):
    """
    Post a tweet, optionally with an image attached.

    """
    if len(text) > 140:
        raise ValueError('tweet is too long')

    auth = twitter.OAuth(
        user_token or os.environ['TWITTER_USER_TOKEN'],
        user_secret or os.environ['TWITTER_USER_SECRET'],
        consumer_key or os.environ['TWITTER_CONSUMER_KEY'],
        consumer_secret or os.environ['TWITTER_CONSUMER_SECRET'])

    image_data, image_id = None, None
    if image_path:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        t_up = twitter.Twitter(domain='upload.twitter.com', auth=auth)
        image_id = t_up.media.upload(media=image_data)['media_id_string']

    if not (text.strip() or image_id):
        raise ValueError('no text or images to tweet')

    t_api = twitter.Twitter(auth=auth)

    params = {
        'status': text,
        'trim_user': True,
    }

    if image_id:
        params.update({
            'media[]': base64.b64encode(image_data),
            '_base64': True,
        })
        return t_api.statuses.update_with_media(**params)
    else:
        return t_api.statuses.update(**params)


def main():
    print('Generating')
    width, height = CANVAS_SIZE
    svg = dust_svg(width, height)

    print('Writing %s' % OUTPUT_SVG_PATH)
    with open(OUTPUT_SVG_PATH, 'w') as svg_file:
        svg_file.write(svg)

    print('Writing %s' % OUTPUT_PNG_PATH)
    with open(OUTPUT_PNG_PATH, 'wb') as png_file:
        subprocess.call(['rsvg-convert', OUTPUT_SVG_PATH], stdout=png_file)

    print('Writing %s' % OUTPUT_CROP_PNG_PATH)
    crop_width, crop_height = CROP_SIZE
    crop_x = (width - crop_width) / 2
    crop_y = (height - crop_height) / 2
    assert crop_x >= 0 and crop_y >= 0
    subprocess.call(['convert', OUTPUT_PNG_PATH, '-crop', '%dx%d+%d+%d'
                     % (crop_width, crop_height, crop_x, crop_y),
                     OUTPUT_CROP_PNG_PATH])

    print('Writing %s' % OUTPUT_JPG_PATH)
    subprocess.call(['convert', OUTPUT_CROP_PNG_PATH, '-quality',
                     str(OUTPUT_JPG_QUALITY), OUTPUT_JPG_PATH])

    if 'tweet' in sys.argv:
        text = choice(EMOJI)
        print('Tweeting')
        post_tweet(text, image_path=OUTPUT_JPG_PATH)

    print('Done')

if __name__ == '__main__':
    sys.exit(main())
