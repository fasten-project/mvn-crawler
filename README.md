# mvn-crawler
This repo contains code for crawling the Maven repos and extracting metadata about projects.
The metadata is gathered from POM files.

*Please note that this repo will probably be temporary.***

## Docker
Build the Docker image:
```
docker build -t maven_crawler .
```

Run the Docker image (example):
```
docker run maven_crawler --m "http://repo2.maven.apache.org/maven2/" --p "./maven2" --c 0.3 --h localhost-30001
```
