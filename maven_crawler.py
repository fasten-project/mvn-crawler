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

# Maven URL: "http://repo2.maven.apache.org/maven2/"

from bs4 import BeautifulSoup
from kafka import KafkaProducer
from urllib.request import urlopen
from urllib.parse import urlparse, urljoin
from os.path import split, exists, join
from os import makedirs
import re
import time
import json
import warnings
import argparse
import requests

# GLOBAL
MVN_PATH = None  # Path to save the maven repos.

# Suppress BeautifulSoup's warnings
#warnings.filterwarnings("ignore", category=UserWarning, module='bs4')


class MavenCoordProducer:
    """
    A Kafka producer for generating Maven coordinates.
    """

    def __init__(self, server_address):
        self.server_address = server_address
        self.kafka_producer = KafkaProducer(bootstrap_servers=[server_address],
                                            value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    def put(self, mvn_coords):
        """
        puts maven coordinates into maven.packages topic
        :param mvn_coords: a dict contains Maven coordinates. e.x. {"groupId": "activecluster",
         "artifactId": "activecluster", "version": "4.0.2", "date": "2011-07-29 13:08"}
        :return:
        """

        self.kafka_producer.send('maven.packages', key=("%s:%s:%s" % (mvn_coords['groupId'], mvn_coords['artifactId'],
                                                                  mvn_coords['version'])).encode('utf-8'),
                                 value=mvn_coords).add_callback(self.on_send_success).add_errback(self.on_send_error)

    def on_send_success(self, record_metadata):
        print(record_metadata.topic)
        print(record_metadata.partition)
        print(record_metadata.offset)

    def on_send_error(self, excp):
        print(excp)


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


def process_pom_file(path):
    """
    Extracts groupID, artifactID and version from a POM file.
    :param path:
    :return:
    """

    pom_file = open(path, 'rb').read()
    soup = BeautifulSoup(pom_file)

    group_id = soup.find('groupid').get_text()
    artifact_id = soup.find('artifactid').get_text()
    version = soup.find('version').get_text()

    return {'groupId': group_id, 'artifactId': artifact_id, 'version': version, 'date': ''}


def extract_pom_files(url, dest, next_sibling, cooldown, mvn_coord_producer):
    """
    It finds and downloads all the POM files same as the Maven repositories' hierarchy.
    :param url:
    :param dest: The path to save the maven dirs
    :param next_sibling:
    :param cooldown:
    :param kafka_producer: An instance of MavenCoordProducer
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
                if not exists(join(MVN_PATH, dest, a['href'])):
                    makedirs(join(MVN_PATH, dest, a['href']))

                #print("Found the url", a['href'])
                extract_pom_files(urljoin(url, a['href']), join(dest, a['href']), a.next_sibling, cooldown, mvn_coord_producer)

            elif bool(re.match(r".+\.pom$", a['href'])):
                #print("Found a POM file: ", a['href'])
                #print("Timestamp: ", next_sibling.split())

                # TODO: For some projects, timestamp is not retrieved properly!
                timestamp = next_sibling.split()
                download_pom(urljoin(url, a['href']), a['href'], join(MVN_PATH, dest))
                mvn_coords = process_pom_file(join(MVN_PATH, dest, a['href']))
                mvn_coords['date'] = timestamp[0] + " " + timestamp[1]

                if mvn_coords['date'] != "- -":
                    print(mvn_coords)
                    mvn_coord_producer.put(mvn_coords)

                #csv_writer[0].writerow([gid, aid, ver, timestamp[0] + " " + timestamp[1]])
                #csv_writer[1].flush()
        else:
            break

        mvn_coord_producer.kafka_producer.flush()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="A Python cralwer for getting Maven coordinates and put them in a Kafka topic.")
    parser.add_argument("--m", required=True, type=str, help="The URL of Maven repositories")
    parser.add_argument("--p", required=True, type=str, help="The local path to save the POM files.")
    parser.add_argument("--c", default=0.5, type=float, help="How longs the crawler waits before sending a request")
    parser.add_argument("--h", default="localhost:9092", type=str, help="The address of Kafka cluster")

    args = parser.parse_args()
    MVN_PATH = args.p

    mvn_producer = MavenCoordProducer(args.h)

    extract_pom_files(args.m, '', None, args.c, mvn_producer)
