FROM python:3

ADD maven_crawler.py /

RUN pip install requests BeautifulSoup4 kafka-python

ENTRYPOINT ["python", "./maven_crawler.py"]
