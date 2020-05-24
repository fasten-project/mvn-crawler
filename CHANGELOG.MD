# Changelog
All notable changes to the Maven Crawler will be documented in this file. The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2020-05-24

### Added
- Adds command line arguments for running the crawler with various options.
- Sends Maven coordinates to a Kafka topic.
- Sends the extracted Maven coordinates as a JSON-compatible string.
- The extracted Maven coordinates have a timestamp based on Unix epochs.
- Avoids downloading and processing POM files if already exists on the disk.
- A non-recursive approach to extract the Maven coordinates.
- Saves and loads the crawled pages from a queue.
- Adds the URL of an extracted POM file to its JSON string.
- Users can set a limit to extract a specified number of Maven coordinates.
- In the case of no Kafka server, the extracted Maven coordinates can be saved in a file.
- Adds a `setup.py` script to install the crawler as a command-line tool.

## Fixed
- Solved the issue of `URLError` while crawling Maven repositories.
- Solved an issue where the artifactID of parent package is extracted from a POM file.
- Solved an issue where a wrong groupID is extracted from a POM file.
- Solved an issue where the JSON string of some Maven coordinates have newlines, tabs or spaces.