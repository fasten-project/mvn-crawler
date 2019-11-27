"""
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
"""

# GLOBAL config
MVN_URL = "http://repo2.maven.apache.org/maven2/"
MVN_PATH = "./maven2"

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse, urljoin
from os.path import split, exists, join
from os import makedirs
import re
import time
import requests


def is_url_file(url):
    """
    Checks whether the url is file or not.
    :param url:
    :return:
    """
    path = urlparse(url).path
    return bool(re.match(r".+\.\w+", split(path)[-1]))


def download_pom(url, pom_file_name, path):
    """
    It downloads a POM file in the specified path
    :param url:
    :param pom_file_name:
    :param path:
    :return:
    """

    response = requests.get(url)
    with open(join(path, pom_file_name), 'wb') as pom_f:
        pom_f.write(response.content)


def extract_pom_files(url, dir, next_sibling, cooldown):
    """
    It finds and downloads all the POM files same as the Maven repositories' hierarchy.
    :param url:
    :param dir:
    :param next_sibling:
    :param cooldown:
    :return:
    """


    # Wait...
    time.sleep(cooldown)

    page_content = urlopen(url).read()
    soup = BeautifulSoup(page_content, 'html.parser')

    # Skips the up level dir (e.g. ../)
    for i, a in enumerate(soup.find_all('a', href=True)[1:]):

        if i <= 5:

            if not is_url_file(a['href']):

                # Create directories same as the Maven's hierarchy
                if not exists(join(MVN_PATH, dir, a['href'])):
                    makedirs(join(MVN_PATH, dir,  a['href']))

                print("Found the url", a['href'])
                extract_pom_files(urljoin(url, a['href']), join(dir, a['href']), a.next_sibling, cooldown)

            elif bool(re.match(r".+\.pom$", a['href'])):
                print("Found a POM file: ", a['href'])
                print("Timestamp: ", next_sibling.split())
                download_pom(urljoin(url, a['href']), a['href'], join(MVN_PATH, dir))
        else:
            break


if __name__ == '__main__':
    extract_pom_files(MVN_URL, '', None, 0.1)
