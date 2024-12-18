"""
A set of Python classes for working with Postman collections import/export format.

Based on the schema v2.1.0 (https://schema.postman.com/)
Can generate a collection from scratch or load from JSON.

Tips:
- When publishing a collection through the API, make sure the info/_postman_id is not set

Known issues:
- Properties with a '-' not currently supported as they are not a valid Python class/field name
  Examples: auth-attribute, proxy-config, protocol-profile-behavior
  --> need to implement a rename in json serializer / deserializer if needed

References:
- https://realpython.com/python-data-classes
- https://stackoverflow.com/questions/3768895/how-to-make-a-class-json-serializable
- https://levelup.gitconnected.com/how-to-deserialize-json-to-custom-class-objects-in-python-d8b92949cd3b
- https://docs.python.org/3/library/dataclasses.html
- https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html

"""
from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Optional, Union

import json
import urllib


#
# DATA CLASSES
#

class CollectionResource(BaseModel):
    """Base class for all Postman collection resource.
    """
    #
    # SERIALIZER
    #
    def toJSON(self, indent=None):
        return self.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)

    def save(self, filepath, indent=4, format="json"):
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(self.model_dump(by_alias=True, exclude_none=True), f, indent=indent)
        else:
            raise ValueError(f"Unsupported format: {format}")

    #
    # DESERIALIZER
    #
    @classmethod
    def from_dict(cls, data: dict) -> Any:
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, json_str: str) -> Collection:
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def load(cls, file_path: str):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return cls.from_dict(data)        

class Auth(CollectionResource):
    type: str = None # apikey, awsv4, basic, bearer, digest, edgegrid, hawk, noauth, oauth1, oauth2, ntlm
    noauth: Optional[None] = None
    apikey: Optional[list['AuthAttribute']] = None
    awsv4: Optional[list['AuthAttribute']] = None
    basic: Optional[list['AuthAttribute']] = None
    bearer: Optional[list['AuthAttribute']] = None
    digest: Optional[list['AuthAttribute']] = None
    edgegrid: Optional[list['AuthAttribute']] = None
    hawk: Optional[list['AuthAttribute']] = None
    ntlm: Optional[list['AuthAttribute']] = None
    oauth1: Optional[list['AuthAttribute']] = None
    oauth2: Optional[list['AuthAttribute']] = None


class AuthAttribute(CollectionResource):
    type: str = None
    key: Optional[str] = None
    value: Optional[str] = None


class Body(CollectionResource):
    mode: Optional[str] = None # raw, urlencoded, formdata, file, graphql
    raw: Optional[str] = None
    graphql: Optional[object] = None
    urlencoded: Optional[list[BodyUrlEncoded]] = None
    formdata: Optional[list[BodyFormData]] = None
    file: Optional[BodyFile]= None
    options: Optional[object] = None
    disabled: Optional[bool] = None


class BodyFile(CollectionResource):
    src: Optional[str] = None
    content: Optional[str] = None

class BodyFormData(CollectionResource):
    key: str = None
    value: Optional[str] = None # for type=text
    src: Optional[Union[list[str],str]] = None # for type=file
    disabled: Optional[bool] = None
    type: Optional[str] = None # test | file
    contentType: Optional[str] = None
    description : Optional[Union['Description',str]] = None

class BodyUrlEncoded(CollectionResource):
    key: str = None
    value: Optional[str] = None
    disabled: Optional[bool] = None
    description: Optional[Union['Description',str]] = None


class Certificate(CollectionResource):
    name: Optional[str] = None
    matches: Optional[list[str]] = None
    key: Optional['CertificateSrc'] = None
    cert: Optional['CertificateSrc'] = None
    passphrase: Optional[str] = None


class CertificateSrc(CollectionResource):
    src: str = None    

class Collection(CollectionResource):
    info: 'Info' = None
    item: list[Union['Item','ItemGroup']] = Field(default_factory=list)
    event: Optional[list['Event']] = None
    variable: Optional[list['Variable']] = None
    auth: Optional['Auth'] = None
    protocolProfileBehavior: Optional[object] = None
    postman_id: Optional[str] = Field(alias="_postman_id", default=None)

    def model_post_init(self, __context):
        if not self.info:
            self.info = Info()        

class Cookie(CollectionResource):
    domain: str = None
    path: str = None
    expires: Optional[str] = None
    maxAge: Optional[str] = None
    hostOnly: Optional[bool] = False
    httpOnly: Optional[bool] = False
    name: Optional[str] = None
    secure: Optional[bool] = False
    session: Optional[bool] = False
    value: Optional[str] = None
    extensions: Optional[list[Any]] = None

class Description(CollectionResource):
    content: str = None
    type: str = None 
    version: Union['Version',str] = None

class Event(CollectionResource):
    listen: str = None
    id: Optional[str] = None
    script: Optional['Script'] = None
    type: Optional[bool] = None


class Header(CollectionResource):
    key: str = None
    value: str = None
    disabled: Optional[bool] = None
    description: Optional[Union['Description',str]] = None

class Info(CollectionResource):
    # schema_field is aliased to schema to prevent naming conflict with Pydantic BaseModel
    name: str = None
    schema_: str = Field(alias='schema', default="https://schema.getpostman.com/json/collection/v2.1.0/collection.json")
    postman_id: Optional[str] = Field(alias='_postman_id', default=None)
    exporter_id: Optional[str] = Field(alias='_exporter_id', default=None) # EXPORTED BUT NOT IN JSON SCHEMA
    collection_link: Optional[str] = Field(alias='_collection_link', default=None) # EXPORTED BUT NOT IN JSON SCHEMA
    description: Optional[Union['Description',str]] = None
    version: Optional[Union['Version',str]] = None
        
class Item(CollectionResource):
    request: 'Request' = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[Union['Description',str]] = None
    variable: Optional[list['Variable']] = None
    event: Optional[list['Event']] = None
    response: Optional[list['Response']] = None
    protocolProfileBehavior: Optional[object] = None

    def model_post_init(self, __context):
        if not self.request:
            self.request = Request()


    """
    Add an event to this item, initializing the event array if needed.
    """
    def add_event(self, event):
        if not self.event:
            self.event = []
        self.event.append(event)

    """
    Helper function to create request
    """
    def create_request(self, url, method='GET'):
        request = Request()
        request.method = method
        request.url = URL()
        url_components = urllib.parse.urlparse(url)
        request.url.protocol = url_components.scheme
        request.url.host = url_components.hostname
        if url_components.port:
            request.url.port = url_components.port
        if len(url_components.path) > 1:
            request.url.path = url_components.path.split('/')[1:]
        if url_components.fragment:
            request.url.hash = url_components.fragment
        self.request = request
        return self.request

    """
    Helper function to create javascript test event
    """
    def create_javascript_test_event(self, script=None):
        event = Event()
        event.script = Script()
        if(script):
            event.script.exec = script
        self.add_event(event)
        return event


class ItemGroup(CollectionResource): # item-group in JSON schema
    item: list['Item'] = Field(default_factory=list)
    name: Optional[str] = None
    description: Optional[Union['Description',str]] = None
    variable: Optional[list['Variable']] = None
    event: Optional[list['Event']] = None
    auth: Optional['Auth'] = None
    protocolProfileBehavior: Optional[object] = None    

class ProxyConfig(CollectionResource): # proxy-config in JSON schema
    match: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    tunnel: Optional[bool] = False
    disabled: Optional[bool] = None

class ProtocolProfileBehavior(CollectionResource): # proxy-profile-behaviour in JSON schema
    # Object with no properties in JSON schema
    pass

class QueryParam(CollectionResource):
    key: str = None
    value: str = None
    disabled: bool = None
    description: Union['Description',str] = None

class Request(CollectionResource):
    url: Optional[Union['URL',str]] = None
    auth: Optional['Auth'] = None
    proxy: Optional['ProxyConfig'] = None
    certificate: Optional['Certificate'] = None
    method: Optional[str] = None # GET,PUT,POST,DELETE,PATCH,HEAD,OPTIONS,PROPFIND,VIEW or custom value
    description: Optional[Union['Description',str]] = None
    header: Optional[Union[list['Header'],str]] = None
    body: Optional['Body'] = None

    def add_header(self, key, value, description=None):
        if not isinstance(self.header, list):
            self.header = []
        self.header.append(Header(key=key, value=value, description=description))

class Response(CollectionResource):
    id: Optional[str] = None
    name: Optional[str] = None # EXPORTED BUT NOT IN JSON SCHEMA
    originalRequest: Optional['Request'] = None
    reponseTime: Optional[Union[str,int]] = None
    timings: Optional[object] = None
    header: Optional[Union[list['Header'],str]] = None
    cookie: Optional[list['Cookie']] = None
    body: Optional[str] = None
    status: Optional[str] = None
    code: Optional[int] = None
    _postman_previewlanguage: Optional[str] = None


class Script(CollectionResource):
    id : Optional[str] = None
    type: Optional[str] = None
    exec: Optional[Union[list[str],str]] = None
    src: Optional[Union[URL,str]] = None
    name: Optional[str] = None

class URL(CollectionResource):
    raw: Optional[str] = None
    protocol: Optional[str] = None
    host: Optional[list[str]] = None
    path: Optional[list[str]] = None
    port: Optional[str] = None
    query: Optional[list['QueryParam']] = None
    hash: Optional[str] = None
    variable: Optional[list['Variable']] = None

    """
    Add a query parameter to this URL, initializing the query array if needed.
    """
    def add_query_param(self, param):
        if not self.query:
            self.query = []
        self.query.append(param)

    """
    Helper function to create a query parameter
    """
    def create_query_parameter(self, key, value=None, description=None, disabled=False):
        param = QueryParam()
        param.key = key
        if value:
            param.value = value
        if description:
            param.description = description
        if disabled:
            param.disabled = disabled
        self.add_query_param(param)
        return param

class Variable(CollectionResource):
    id: Optional[str] = None
    key: Optional[str] = None
    value: Optional[Any] = None
    type: Optional[str] = None # string, boolean, any, number
    name: Optional[str] = None
    description: Optional[Union['Description',str]] = None
    system: Optional[bool] = None
    disabled: Optional[bool] = None

class Version(CollectionResource):
    major: int = 0
    minor: int = 0
    patch: int = 0
    identifier: Optional[str] = None
    meta: Optional[Any] = None

