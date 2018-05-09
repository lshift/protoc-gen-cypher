# protobuf2cypher

A tool to produce neo4j graphs from protobuf/gRPC files.

## The short way

    docker build --tag protobuf2cypher .
    # need to mount the output and input directories
    docker run \
        --mount type=bind,src=$PWD/generated,dst=/generated \
        --mount type=bind,src=$PWD/../../protobuf,dst=/protobuf \
        protobuf2cypher

## The long way

Requires python 3.6 (or a venv)
    
    pip install -r requirements.txt
 
See Dockerfile to download protoc to this directory 

Then

    PSRC=test  # top level directory of the protobuf files
    mkdir -p generated
    ./bin/protoc \
        --plugin=protoc-gen-cypher=./protobuf2cypher.py \
        --cypher_out=generated \
        --proto_path=$PSRC \
        $PSRC/protobuf/**/*.proto
    
Cypher file will now be in the directory "generated" 