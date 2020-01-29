"""
This module reads POM files locally from the file system and puts Maven coordinates into the Kafka topic
"""

from urllib.request import urlopen
from urllib.parse import urljoin
from datetime import datetime
from os.path import join, basename
from mvn_crawler.maven_crawler import MavenCoordProducer, process_pom_file, MVN_URL
import argparse
import os
import traceback


# https://repo1.maven.org/

def get_timestamp_pom(pom_file_url):
    """
    Gets timestamp from the last modified date of the POM file on the server.
    :param pom_file_url:
    :return:
    """

    f = urlopen(pom_file_url)
    return int(datetime.strptime(f.headers['last-modified'], '%a, %d %b %Y %H:%M:%S GMT').timestamp())


def extract_pom_local(repos_path, mvn_producer):

    # A file save POM files that could not be sent
    f_error_pom = open('errors_poms.txt', 'a')
    f_processed_pom = open('processed_poms.txt', 'a+')

    processed_poms = f_processed_pom.read().splitlines()
    print(processed_poms)

    for root, dirs, files in os.walk(repos_path):
        for f in files:
            if f.endswith(".pom"):

                try:

                    if join(root, f) not in processed_poms:
                        print(join(root, f))
                        maven_cord = process_pom_file(os.path.join(root, f))
                        if maven_cord is not None:
                            print(urljoin(MVN_URL, join(root, f).split('maven2/')[1]))
                            maven_cord['date'] = get_timestamp_pom(urljoin(MVN_URL, join(root, f).split('maven2/')[1]))

                            mvn_producer.put(maven_cord)
                            mvn_producer.kafka_producer.flush()

                            f_processed_pom.write(join(root, f) + '\n')

                except Exception:
                    traceback.print_exc()
                    f_error_pom.write(join(root, f) + '\n')

    f_error_pom.close()
    f_processed_pom.close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Reads Maven coordinates locally and puts them in a Kafka topic.")
    parser.add_argument("--p", required=True, type=str, help="The local path to save the POM files.")
    parser.add_argument("--h", default="localhost:9092", type=str, help="The address of Kafka cluster")
    args = parser.parse_args()

    mvn_producer = MavenCoordProducer(args.h)

    extract_pom_local(args.p, mvn_producer)
