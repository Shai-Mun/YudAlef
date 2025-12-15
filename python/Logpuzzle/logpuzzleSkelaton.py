import os
import re
import sys,subprocess
from urllib.request import urlretrieve


def read_urls(filename):
    """Returns a list of the puzzle urls from the given log file,
    extracting the hostname from the filename itself.
    Screens out duplicate urls and returns the urls sorted into
    increasing order."""
    with open(filename, 'r') as f:
        data = f.read()

    urls = list(set(re.findall('GET /cyberbit/.*HTTP/1..', data)))
    urls.sort(key=lambda x: x[x.rfind('-')+1:x.rfind('.')], )
    return urls


def download_images(img_urls, dest_dir, src_file):
    """Given the urls already in the correct order, downloads
    each image into the given directory.
    Gives the images local filenames img0, img1, and so on.
    Creates an index.html in the directory
    with an img tag to show each local image file.
    Creates the directory if necessary.
    """

    count = 0
    for img_url in img_urls:
        url = f'https://{src_file[:-4]}/{img_url[4:img_url.find('HTTP')-1]}'
        urlretrieve(url, f'{dest_dir}{count}.jpg')
        count += 1
    return count


def write_html(dest_dir, count):
    html = "<html><head><title>Site Name</title></head><body>"

    for i in range(count):
        html += f"<img src=\"{dest_dir}{i}.jpg\"/>"

    html += "</body></html>"

    with open("index.html", 'w') as f:
        f.write(html)


def main():
    if len(sys.argv) < 3:
        print('usage: <log filename> <target location> ')
    else:
        print('start')
        log_filename = sys.argv[1]
        target_dir = sys.argv[2]

        img_urls = read_urls(log_filename)

        print(img_urls)

        count = download_images(img_urls, target_dir, log_filename)
        print('Done')
        write_html(target_dir, count)
        subprocess.call('index.html', stdin=None, stdout=None, stderr=None, shell=True)


if __name__ == '__main__':
    main()
