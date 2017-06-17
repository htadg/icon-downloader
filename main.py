#!usr/bin/python

from __future__ import print_function

import os
import re
import six
from random import randint

import argparse
import requests
from clint.textui import progress
from lxml import html

if six.PY2:
    import urlparse
else:
    import urllib.parse as urlparse


def get_download_url(url, size=512, flag=False):
    global base_url
    path = url
    if flag:
        components = url.split('/')
        path = components[0] + \
            '/{}x{}/'.format(size, size) + '/'.join(components[1:])
    return urlparse.urljoin(base_url, path)


def make_dir(name):
    global down_path
    path = os.path.join(down_path, name)
    if not os.path.exists(path):
        os.mkdir(path)


def download_url(url, title=None, ext=None, dim=None, path=None):
    try:
        if not path:
            file_name = url.split('/')[-1].split('.')[0]
            reg = re.compile('\_?[^0-9a-zA-Z]?([a-zA-z]+)[^0-9a-zA-z]?\_?')
            res = re.search(reg, file_name)
            file_name = res.groups()[0].strip('_') + '.' + ext
            path = os.path.join(os.path.join(title, os.path.join(
                ext, '{}x{}'.format(dim, dim))), file_name)
            path = os.path.join(down_path, path)
        if os.path.exists(path):
            ext = path.split('.')[-1]
            name = '.'.join(path.split('.')[:-1]) + '_' + str(count)
            path = name + '.' + ext
            download_url(url, path=path)
        else:
            r = requests.get(url, stream=True)
            print('[Downloading]: ' + path)
            with open(path, 'wb') as f:
                total_length = int(r.headers.get('content-length'))
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()
    except Exception as e:
        print('[ERROR]: {} -- {}'.format(e, url))


def download(url, page=None):
    global count
    if page is None:
        page = requests.get(url)
    tree = html.fromstring(page.content)
    container = tree.xpath('//div[@class="page-container"]')[0]

    title = container.xpath('.//h1[contains(@class, "page-title")]/text()')[0]

    icons = container.xpath(
        './/ul[contains(@class, "icon-lists")]/li[@class="icon"]')

    for icon in icons:
        available = icon.xpath(
            './/p[@class="button"]/a[not(text()="MORE")]/@href')
        count += 1
        for extension in available:
            ext = extension.split('.')[-1]
            if ext in formats:
                for dim in dims:
                    if ext == "png":
                        url = get_download_url(extension, dim, True)
                    else:
                        url = get_download_url(extension)
                    download_url(url, title, ext, dim)

def main():

    page = requests.get(url)
    tree = html.fromstring(page.content)
    container = tree.xpath('//div[@class="page-container"]')[0]

    title = container.xpath('.//h1[contains(@class, "page-title")]/text()')[0]

    make_dir(title)
    for ext in formats:
        path = os.path.join(down_path, title)
        dir_name = os.path.join(path, ext)
        make_dir(dir_name)
        for dim in dims:
            dim_dir_name = os.path.join(dir_name, '{}x{}'.format(dim, dim))
            make_dir(dim_dir_name)


    pages = container.xpath(
        './/ul[@class="pagination"]/li[not(@class="active")]/a/@href')

    download(url, page)
    for page in pages:
        download(get_download_url(page))

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description='Download icons from https://shareicon.net')
parser.add_argument(
    '-u', '--url', type=str, help='Iconset URL', required=True)
parser.add_argument(
    '-p', '--path', type=str, help='Path to save the icons', required=False,
    default='.')
parser.add_argument('-f', '--format', nargs='+',
                    help='Format of the icon to download (Available choices: png, svg, icns, ico)',
                    type=str,
                    default=["ico"],
                    required=False)
parser.add_argument('-s', '--dimensions', nargs='+',
                    help='Dimension of the icon to download (Available choices: 12, 16, 32, 48, 64, 128, 256, 512)',
                    type=int,
                    default=[512],
                    required=False)

args = parser.parse_args()
url = args.url
down_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), args.path)
dims = args.dimensions
formats = args.format

parsed_uri = urlparse.urlparse(url)
base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

count = 0

if __name__ == '__main__':
    main()
