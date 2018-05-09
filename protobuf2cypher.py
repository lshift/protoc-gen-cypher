#!/usr/bin/env python3

import sys

from google.protobuf.compiler import plugin_pb2 as plugin
from typing import Dict, Iterator

# type defs
Options = Dict[str, str]
OutLines = Iterator[str]


def log(message):
    print(message, file=sys.stderr)


def main():
    # Read request protobuf message from stdin and parse
    data = sys.stdin.buffer.read()
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)
    # log("request options: %r"% request.parameter)
    # assume no spaces around options and key and vals do not contain '"' or ','
    if request.parameter:
        options = {k:v for k,v in (opt.split('=') for opt in request.parameter.split(','))}
    else:
        options = {*()}  # https://twitter.com/raymondh/status/980864744549576704
    # log("request options: %r"% options)

    # Create new response object to fill in and return to the caller
    response = plugin.CodeGeneratorResponse()

    # Generate cypher statements. We're only going to produce one file
    content = generate_code(request, options)
    f = response.file.add()
    f.name = 'proto.cql'
    f.content = '\n'.join(content)

    # Serialise and return response protobuf message to caller
    output = response.SerializeToString()
    sys.stdout.buffer.write(output)


def fixname(name):
    return name.replace('.', '_');


def node(t, package, name):
    package = fixname(package)
    name = fixname(name)
    longname = f'{package}_{name}'
    return f'CREATE ({longname}:{t} {{longname: \'{longname}\', package:\'{package}\', name:\'{name}\'}})'


def link(link_type, me, them):
    cql = 'MATCH (a),(b)'
    cql += f' WHERE a.longname = \'{fixname(me)}\''
    cql += f' AND b.longname = \'{fixname(them)}\''
    cql += f' CREATE (a)-[:{link_type}]->(b)'
    return cql


def generate_code(request, options: Options) -> OutLines:
    """
    NB. this function is a generator.

    :param request: a CodeGeneratorRequest object (or duck-type)
    :param options: an Options dict
    """
    links = []
    for file in request.proto_file:
        for line in generate_nodes(file, options, links):
            yield line

    for (link_type, message_type, field_name, field_type) in links:
        yield(link(link_type, message_type, field_type))

    yield ''


def generate_nodes(proto_file, options: Options, links) -> OutLines:
    """
    NB. this function is a generator.

    :param proto_file: a FileDescriptorProto object (or duck-type)
    :param options: an Options dict
    """

    for m in proto_file.message_type:
        message_type = f'{proto_file.package}.{m.name}'
        yield node('Message', proto_file.package, m.name)

        for f in m.field:
            # yield(f.name) TODO, add to node
            field_type = f.type_name[1:]
            if field_type != '':
                links.append(('Contains', message_type, f.name, field_type))


    # if 'noservices' not in options:
    #     for s in proto_file.service:
    #         for m in s.method:
    #             method_name = f'{proto_file.package}.{s.name}.{m.name}'
    #             yield(f'[{method_name}] {{color: orange}}')
    #             yield(m.input_type[1:])
    #             yield(m.output_type[1:])
    #             yield(f'[{method_name}] *--1 [{m.input_type[1:]}]')
    #             yield(f'[{method_name}] 1--* [{m.output_type[1:]}]')

    for e in proto_file.enum_type:
        yield node('Enum', proto_file.package, e.name)


if __name__ == '__main__':
    main()
