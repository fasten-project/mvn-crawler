"""
This module reads POM files locally from the file system and puts Maven coordinates into the Kafka topic
"""

from mvn_crawler.maven_crawler import MavenCoordProducer
import argparse
import os


def extract_pom_local(repos_path):

    for root, dirs, files in os.walk(repos_path):
        for f in files:
            if f.endswith(".pom"):
                print(os.path.join(root, f))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Reads Maven coordinates locally and puts them in a Kafka topic.")
    parser.add_argument("--p", required=True, type=str, help="The local path to save the POM files.")
    parser.add_argument("--h", default="localhost:9092", type=str, help="The address of Kafka cluster")
    args = parser.parse_args()

    mvn_producer = MavenCoordProducer(args.h)

    extract_pom_local(args.p)
