# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: unary.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bunary.proto\x12\x05unary\"\x1c\n\x08Response\x12\x10\n\x08response\x18\x01 \x01(\t\"#\n\x0bJsonAddress\x12\x14\n\x0cjson_address\x18\x01 \x01(\t\"\x1d\n\x08JsonDati\x12\x11\n\tjson_data\x18\x01 \x01(\t\"\x14\n\x04Nomi\x12\x0c\n\x04nomi\x18\x01 \x01(\t2:\n\x0cImageService\x12*\n\nUploadFile\x12\x0f.unary.JsonDati\x1a\x0b.unary.Nomi2@\n\x0c\x45mailService\x12\x30\n\tSendEmail\x12\x12.unary.JsonAddress\x1a\x0f.unary.Responseb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'unary_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _RESPONSE._serialized_start=22
  _RESPONSE._serialized_end=50
  _JSONADDRESS._serialized_start=52
  _JSONADDRESS._serialized_end=87
  _JSONDATI._serialized_start=89
  _JSONDATI._serialized_end=118
  _NOMI._serialized_start=120
  _NOMI._serialized_end=140
  _IMAGESERVICE._serialized_start=142
  _IMAGESERVICE._serialized_end=200
  _EMAILSERVICE._serialized_start=202
  _EMAILSERVICE._serialized_end=266
# @@protoc_insertion_point(module_scope)