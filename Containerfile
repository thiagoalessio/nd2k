FROM docker.io/library/python:3.10-slim
COPY ./dist ./dist
RUN pip install ./dist/nd2k-*.tar.gz && rm -r ./dist
ENTRYPOINT ["nd2k"]
