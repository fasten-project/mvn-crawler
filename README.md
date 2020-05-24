# Maven Crawler
This is a tool for crawling Maven repositories and gathering Maven coordinates.
It can be used for research and education purposes.

# Installation
## Requirements

- Python 3.5 or newer
- [Apache Kafka](https://kafka.apache.org/quickstart) (**optional**)

## Quick install
```
pip install mvncrawler
```


# Usage
```
mvncrawler --p ./maven/ --q q_items.txt  --t "fasten.mvn.pkg" --c 5 --l 10
```
It extracts 10 Maven coordinates. 
- Use `--help` option to see the description of each arguments.
- If you do not have a Kafka server on your machine, add `--no-kafka` option to the tool for saving Maven coordinates in a file.
- You can remove `--l 10` option to extract Maven coordinates without a limit.

# Output format
Extracted Maven coordinates are converted to a JSON-compatible string as shown and described below:
```
{"groupId": "com.yahoo.vespa", "artifactId": "zookeeper-server-common", "version": "7.171.10", "date": "1580860140", "url": "https://repo1.maven.org/maven2/com/yahoo/vespa/zookeeper-server-common/7.171.10/zookeeper-server-common-7.171.10.pom"}
```

- `groupId`: The specified groupID in a POM file.
- `artifactId`: The specified artifactID in a POM file.
- `version`: The version of a Maven package as specified in its POM file.
- `date`: The release date of a Maven package in Unix epoch format.
- `url`: The URL of a POM file on the Maven server.

# Disclaimer
We are NOT responsible for any damage or the misuse of this tool.
