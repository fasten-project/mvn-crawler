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

from bs4 import BeautifulSoup
from kafka import KafkaProducer
from urllib.request import urlopen
from urllib.parse import urlparse, urljoin
from urllib.error import URLError
from os.path import split, exists, join, isfile
from collections import deque
from os import makedirs
from datetime import datetime
import re
import csv
import time
import sys
import json
import argparse
import requests

# GLOBAL
MVN_PATH = None  # Path to save the maven repos.
MVN_URL = "https://repo1.maven.org/maven2/"


class MavenCoordProducer:
    """
    A Kafka producer for generating Maven coordinates.
    """

    def __init__(self, server_address, topic):
        self.server_address = server_address
        self.kafka_producer = KafkaProducer(bootstrap_servers=[server_address],
                                            value_serializer=lambda m: json.dumps(m).encode('utf-8'), api_version=(2,2,0))
        self.topic = topic

    def put(self, mvn_coords):
        """
        puts maven coordinates into maven.packages topic
        :param mvn_coords: a dict contains Maven coordinates. e.x. {"groupId": "activecluster",
         "artifactId": "activecluster", "version": "4.0.2", "date": "2011-07-29 13:08"}
        :return:
        """

        self.kafka_producer.send(self.topic, key=("%s:%s:%s" % (mvn_coords['groupId'], mvn_coords['artifactId'],
                                                                  mvn_coords['version'])).encode('utf-8'),
                                 value=mvn_coords).add_callback(self.on_send_success).add_errback(self.on_send_error)

    def on_send_success(self, record_metadata):
        print(record_metadata.topic)
        print(record_metadata.partition)
        print(record_metadata.offset)

    def on_send_error(self, excp):
        print(excp)


class PageLink:
    """
    Encapsulates a page link with its url, file hierarchy, and timestamp
    """

    def __init__(self, url, file_h, timestamp):
        self.url = url
        self.file_h = file_h
        self.timestamp = timestamp


def url_last_part(url):
    """
    Returns last part of a URL.
    E.g. http://repo2.maven.apache.org/maven2/HTTPClient/HTTPClient/0.3-3/HTTPClient-0.3-3.pom -> HTTPClient-0.3-3.pom
    :param url:
    :return:
    """
    return split(urlparse(url).path)[-1]


def is_url_file(url):
    """
    Checks whether the url is file or not.
    :param url:
    :return:
    """
    return bool(re.match(r".+\.\w+", url_last_part(url)))


def download_pom(url, path):
    """
    It downloads a POM file in the specified path
    :param url:
    :param pom_file_name:
    :param path:
    :return:
    """

    response = requests.get(url)
    with open(path, 'wb') as pom_f:
        pom_f.write(response.content)


def convert_to_unix_epoch(datetime_str):
    """
    Converts Maven's timestamps to UNIX epochs
    :param datetime_str:
    :return:
    """

    date, time = datetime_str.split(" ")
    year, month, day = date.split("-")
    hour, min = time.split(":")

    return int(datetime(int(year), int(month), int(day), int(hour), int(min)).timestamp())


def process_pom_file(path):
    """
    Extracts groupID, artifactID and version from a POM file.
    :param path:
    :return:
    """

    pom_file = open(path, 'rb').read()
    soup = BeautifulSoup(pom_file)

    group_id = None
    version = soup.find('version')
    artifact_id = None
    #packaging = soup.find('packaging')

    # Fixes a case where a wrong groupID is extracted from the parent tag.
    for g in soup.find_all('groupid'):
        if g.parent.name == 'project':
            group_id = g
            break
        elif g.parent.name == 'parent':
            group_id = g

    # TODO: Fix the case where the artifactID is extracted from the parent tag.
    for a in soup.find_all('artifactid'):
        if a.parent.name == 'project':
            artifact_id = a
            break

    if group_id is not None and artifact_id is not None and version is not None:

        # TODO: Consider only POM files that have packaging: [jar, war, ear]
        # There are cases where packaging tag is not present in the POM file but the package has a JAR file.
        #if packaging is None or packaging.get_text() in ('jar', 'war', 'ear'):
        return {'groupId': validate_str(group_id.get_text()), 'artifactId': validate_str(artifact_id.get_text()),
                'version': validate_str(version.get_text()), 'date': '', 'url': ''}
    else:
        return None


def validate_str(str):
    """
    This removes all the spaces, new line and tabs from a given string
    :param str:
    :return:
    """
    return ''.join(str.split())


def save_queue(items, path):
    """
    It saves the queue items on the disk.
    :param items:
    :param path:
    :return:
    """

    with open(path, 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(items)


def load_queue(path):
    """
    Loads the items of a queue file into a list
    :param path:
    :return:
    """

    with open(path, 'r') as f:
        reader = csv.reader(f)
        items = [PageLink(i[0], i[1], i[2]) for i in reader]

    return items


def create_queue_after(after_org_name):
    """
    This creates a new queue after a specified org or a url.
    :param after_org_name:
    :return:
    """

    found_org_name = False
    extracted_links = []
    for u in extract_page_links(MVN_URL):

        if u['href'] == after_org_name:
            found_org_name = True
            print("Found name")

        if found_org_name:
            if "/" in u['href']:
                extracted_links.append([urljoin(MVN_URL, u['href']), u['href'], u.next_sibling.strip()])

    save_queue(extracted_links, "./q_items_new.txt")


def create_queue(url):
    """
    This creates a queue of given a URL.
    :param url:
    :return:
    """

    return [[urljoin(MVN_URL, u['href']), u['href'], u.next_sibling.strip()]for u in extract_page_links(urljoin(MVN_URL,
                                                                                                                url))[1:]]


def extract_pom_files(url, dest, queue_file, cooldown, mvn_coord_producer, limit):
    """
    Extracts the POM files from given maven repository and puts them in a Kafka topic. It is a non-recursive approach
    and uses a queue.
    :param url:
    :param dest:
    :param next_sibling:
    :param cooldown:
    :param mvn_coord_producer: An instance of MavenCoordProducer
    :param limit: Number of POM files to be extracted
    :return:
    """

    if exists(queue_file):
        q = deque(load_queue(queue_file))
        print("Loaded the queue items from the file...")
    else:
        links_list = [PageLink(urljoin(url, u['href']), u['href'], u.next_sibling.strip()) for u in extract_page_links(url)[1:]]
        q = deque(links_list)
        save_queue([[i.url, i.file_h, i.timestamp] for i in links_list], queue_file)
        print("Downloaded and saved the queue....")

    num_pom_ext = 0
    limit_condition = lambda: num_pom_ext < limit if limit > 0 else lambda: True

    while len(q) != 0 and limit_condition():

        # Picks one item from the beginning of the queue
        u = q.popleft()
        print("URL:", u.url, " | ", "FH: ", u.file_h, " | ", "TS: ", u.timestamp)
        if not is_url_file(u.url):
            #print("Path: ", join(MVN_PATH, u.file_h))
            # Create directories same as the Maven's hierarchy
            if not exists(join(dest, u.file_h)):
                makedirs(join(dest, u.file_h))

            # Wait before sending a request
            time.sleep(cooldown)

            page_links = extract_page_links(u.url)

            if page_links is not None:

                # Skips the up-level dir. (e.g. \..)
                for pl in page_links[1:]:
                    #print("URL:", urljoin(u.url, pl['href']), "FH: ", join(u.file_h, pl['href']), "TS: ", pl.next_sibling.strip())

                    q.appendleft(PageLink(urljoin(u.url, pl['href']), join(u.file_h, pl['href']), pl.next_sibling.strip()))

        elif bool(re.match(r".+\.pom$", u.url)):
            print("Found a POM file: ", u.url)

            # Checks whether the POM file is already downloaded.
            if not isfile(join(dest, u.file_h)):

                download_pom(u.url, join(dest, u.file_h))
                print("Downloaded %s" % join(dest, u.file_h))

            else:
                print("File %s exits." % join(dest, u.file_h))

            mvn_coords = process_pom_file(join(dest, u.file_h))

            # Puts Maven coordinates into the Kafka topic if the POM file is valid
            # A valid POM file should have groupID, artifactID, and version.
            if mvn_coords is not None:

                # TODO: For some projects, timestamp is not retrieved properly!
                timestamp = u.timestamp.split()
                mvn_coords['date'] = timestamp[0] + " " + timestamp[1]
                mvn_coords['url'] = u.url  # POM file URL

                if mvn_coords['date'] != "- -":

                    mvn_coords['date'] = str(convert_to_unix_epoch(mvn_coords['date']))
                    print("cord: %s | t: %s " % (mvn_coords['groupId'] + ":" + mvn_coords['artifactId'] + ":" +
                                                 mvn_coords['version'], mvn_coords['date']))
                    mvn_coord_producer.put(mvn_coords)
                    mvn_coord_producer.kafka_producer.flush()
                    num_pom_ext += 1

                else:
                    print("A pom file without timestamp!")
                    print("cord: %s | t: %s " % (mvn_coords['groupId'] + ":" + mvn_coords['artifactId'] + ":" +
                                                 mvn_coords['version'], mvn_coords['date']))

            else:
                print("Skipped - not a valid POM file - %s\n" % u.url)

        save_queue([[items.url, items.file_h, items.timestamp] for items in list(q)], queue_file)


def extract_page_links(url):
    """
    Extracts all the links in a web page.
    :param url:
    :return:
    """

    try:
        page_content = urlopen(url).read()
        soup = BeautifulSoup(page_content, 'html.parser')
        return soup.find_all('a', href=True)

    except URLError:

        print("Cannot explore this path: %s" % url)
        return None


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="A crawler for gathering Maven coordinates and put them in a Kafka topic.")
    parser.add_argument("--m", default=MVN_URL, type=str, help="The URL of Maven repositories")
    parser.add_argument("--p", required=True, type=str, help="A path to save the POM files on the disk")
    parser.add_argument("--q", required=True, type=str, help="The file of queue items")
    parser.add_argument("--c", default=0.5, type=float, help="How long the crawler waits before sending a request")
    parser.add_argument("--t", default="fasten.mvn.pkg", type=str, help="The name of a Kafka topic to put Maven coordinates into.")
    parser.add_argument("--h", default="localhost:9092", type=str, help="The address of Kafka server")
    parser.add_argument("--l", default=-1, type=int, help="The number of POM files to be extracted. -1 means unlimited.")

    args = parser.parse_args()
    MVN_PATH = args.p

    mvn_producer = MavenCoordProducer(args.h, args.t)
    extract_pom_files(args.m, MVN_PATH, args.q, args.c, mvn_producer, args.l)
