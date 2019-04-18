FROM python:3

ADD connection.py /
ADD dnsconfig.py /
ADD listener.py /
# RUN apt-get update && apt-get install -y dnsutils
EXPOSE 53/udp

CMD [ "python", "./listener.py" ]
