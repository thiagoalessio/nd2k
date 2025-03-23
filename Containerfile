FROM docker.io/library/python:3.11.11-alpine
COPY ./dist ./dist
RUN pip install ./dist/nd2k-*.tar.gz && rm -r ./dist
ENTRYPOINT ["nd2k"]
