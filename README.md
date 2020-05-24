# maven-crawler
This repo contains code for crawling the Maven repos and extracting metadata about projects.
The metadata is gathered from POM files.


## Run 
To start the Maven crawler on Linux in background, run the following command:
```
nohup python maven_crawler.py --m "https://repo1.maven.org/maven2/" --p "./maven2" --q q_items.txt --c 5 --h localhost:30001 &
```
To extracted a limited number of Maven coordinates, run below command:
```
nohup python maven_crawler.py --m "https://repo1.maven.org/maven2/" --p "./maven2" --q q_items.txt --c 5 --h localhost:30001 --l 10 &
```
The above command extracts only 10 Maven coordinates and saves the queue in the current working directory. To change the limit, assign a positive value to arg `--l`.

## Docker
Build the Docker image:
```
docker build -t maven_crawler .
```

To start the crawler and extract 10 Maven coordinates, run the following command based on your OS:

* **Linux**:
```
docker run --network="host" --it maven_crawler --m "https://repo1.maven.org/maven2/" --p "./maven2" --q q_items.txt --c 5 --t maven.packages --h localhost:9092 --l 10
```
* **macOS**:
```
docker run --it maven_crawler --m "https://repo1.maven.org/maven2/" --p "./maven2" --q q_items.txt --c 5 --t maven.packages --h host.docker.internal:9092 --l 10
```

To crawl the entire Maven repos, remove `--l` arg from the above commands.
