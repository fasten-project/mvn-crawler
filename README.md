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

# Disclaimer
We are NOT responsible for any damage or the misuse of this tool.
