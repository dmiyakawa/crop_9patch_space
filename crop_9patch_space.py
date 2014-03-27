#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import os.path
import shlex
import subprocess
import sys
import traceback

def do_crop(src_path, dst_path, basename, spec, temp_dir):
    center_width = spec['width'] - spec['x_crop']*2 - 2
    center_x_offset = 1 + spec['x_crop']
    right_x_offset = spec['width'] - 1
    middle_y_offset = 1 + spec['y_crop']
    middle_height = spec['height'] - spec['y_crop']*2 - 2
    bottom_y_offset = spec['height'] - 1
    crop_args = [('top.left', '1x1+0+0!'),
                 ('top.center', '{}x1+{}+0!'.format(center_width, center_x_offset)),
                 ('top.right', '1x1+{}+0!'.format(center_x_offset)),
                 ('middle.left', '1x{}+0+{}!'.format(middle_height, middle_y_offset)),
                 ('middle.center', '{}x{}+{}+{}!'.format(center_width, middle_height,
                                                         center_x_offset, middle_y_offset)),
                 ('middle.right', '1x{}+{}+{}!'.format(middle_height,
                                                       right_x_offset, middle_y_offset)),
                 ('bottom.left', '1x1+0+{}!'.format(bottom_y_offset)),
                 ('bottom.center', '{}x1+{}+{}!'.format(center_width, center_x_offset,
                                                        bottom_y_offset)),
                 ('bottom.right', '1x1+{}+{}!'.format(right_x_offset, bottom_y_offset))]
    for (crop_name, crop_spec) in crop_args:
        # print(crop_name, file=sys.stderr)
        temp_name = '{}.{}.png'.format(basename, crop_name)
        temp_path = os.path.join(temp_dir, temp_name)
        cmd = ('convert {}'
               ' -background none -regard-warnings'
               ' -crop {} PNG32:{}').format(src_path, crop_spec, temp_path)
        p = subprocess.Popen(shlex.split(cmd),
                             stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE)
        p.wait()
        if p.returncode:
            print('Failed to execute "{}"'.format(cmd), file=sys.stderr)
            print('Returned "{}"'.format(p.returncode), file=sys.stderr)
            print('{}\n'.format(p.stdout.read()), file=sys.stderr)
            return False

    intermediate_files = map(lambda x: os.path.join(temp_dir, '{}.{}.png'.format(basename, x[0])),
                             crop_args)
    dir_path = os.path.dirname(os.path.realpath(dst_path))
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    try:
        cmd = (('montage {} -background none'
                ' -regard-warnings -geometry \'+0+0\' PNG32:{}')
               .format(' '.join(intermediate_files), dst_path))
        p = subprocess.Popen(shlex.split(cmd),
                             stderr=subprocess.STDOUT,
                             stdout=subprocess.PIPE)
        p.wait()
        if p.returncode:
            print('Failed to execute "{}"'.format(cmd), file=sys.stderr)
            print('Returned "{}"'.format(p.returncode), file=sys.stderr)
            print('{}\n'.format(p.stdout.read()), file=sys.stderr)
            return False
    except Exception as e:
        print('Failed to execute "{}"'.format(cmd), file=sys.stderr)
        print('Exception raised:{}'.format(traceback.format_exc()), file=sys.stderr)
        return False
    return True


def do_main(src, dst, temp_dir):
    dpi_specs = {'mdpi': {'width': 28, 'height': 34, 'x_crop': 4, 'y_crop': 4},
                 'hdpi': {'width': 41, 'height': 50, 'x_crop': 6, 'y_crop': 6},
                 'xhdpi': {'width': 54, 'height': 66, 'x_crop': 8, 'y_crop': 8},
                 'xxhdpi': {'width': 80, 'height': 98, 'x_crop': 12, 'y_crop': 12},
    }
    state_list = ['normal', 'disabled', 'pressed', 'focused', 'disabled_focused']

    basename_tmpl = 'btn_default_{}_holo_light'
    for (dpi, spec) in dpi_specs.iteritems():
        for state in state_list:
            basename = basename_tmpl.format(state)
            dpi_dir = 'drawable-{}'.format(dpi)

            src_name = basename + '.9.png'
            src_path = os.path.join(src, dpi_dir, src_name)
            dst_name = basename + '_cropped.9.png'
            dst_path = os.path.join(dst, dpi_dir, dst_name)
            if not do_crop(src_path, dst_path, basename, spec, temp_dir):
                return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=u'Crops button\'s edge')
    parser.add_argument('src', metavar='src',
                        type=str, nargs=1,
                        help='Source directory that contains drawable-Ndpi/ directories')
    parser.add_argument('dst', metavar='dest',
                        type=str, nargs=1,
                        help='Destination directory that contains drawable-Ndip/ directories')
    parser.add_argument('--temp-dir', '-t',
                        action='store',
                        type=str,
                        default='/tmp',
                        help='Working directory where a lot of gabage will be stored')
    args = parser.parse_args()
    do_main(args.src[0], args.dst[0], args.temp_dir)

