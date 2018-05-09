
# ToDo might be useful if we had a pre-built java8+python3+protoc docker base image lying around...
FROM python:3.6.4


# download external tools
WORKDIR /work/bin
RUN apt-get update

# protoc
ENV PROTOBUF_VERSION=3.5.1 PROTOBUF_ARCH=x86_64 PROTOBUF_OS=linux
RUN apt-get install -y unzip && \
    wget https://github.com/google/protobuf/releases/download/v${PROTOBUF_VERSION}/protoc-${PROTOBUF_VERSION}-${PROTOBUF_OS}-${PROTOBUF_ARCH}.zip && \
    unzip protoc-${PROTOBUF_VERSION}-${PROTOBUF_OS}-${PROTOBUF_ARCH}.zip && \
    rm protoc-${PROTOBUF_VERSION}-${PROTOBUF_OS}-${PROTOBUF_ARCH}.zip

# copy in source and install python deps
WORKDIR /work
COPY . protobuf2cypher
RUN pip install -r protobuf2cypher/requirements.txt


# /generated and /protobuf must be mounted by the `docker run` command
ENTRYPOINT /work/bin/bin/protoc --plugin=protoc-gen-cypher=/work/protobuf2cypher/protobuf2cypher.py --cypher_out=/generated --proto_path=/protobuf /protobuf/**/*.proto

