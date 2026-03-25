"""
A set of Python classes for working with Postman collections import/export format.

Based on the schema v2.1.0 (https://schema.postman.com/)
Can generate a collection from scratch or load from JSON.

Tips:

- When publishing a collection through the API, make sure the info/_postman_id is not set

Known issues:

- Properties with a '-' not currently supported as they are not a valid Python class/field name
  Examples: auth-attribute, proxy-config, protocol-profile-behavior.
  --> need to implement a rename in json serializer / deserializer if needed


"""

from __future__ import annotations

import json
import urllib
from typing import Any

from pydantic import BaseModel, Field, field_validator

#
# DATA CLASSES
#


class CollectionResource(BaseModel):
    """Base class for all Postman collection resource."""

    #
    # SERIALIZER
    #

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True)

    def to_json(self, indent: int | None = None) -> str:
        return self.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True, indent=indent)

    def save(self, filepath, indent=4, format="json"):
        if format == "json":
            with open(filepath, "w") as f:
                json.dump(self.model_dump(by_alias=True, exclude_none=True), f, indent=indent)
        else:
            raise ValueError(f"Unsupported format: {format}")

    #
    # DESERIALIZER
    #
    @classmethod
    def from_dict(cls, data: dict) -> CollectionResource:
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, json_str: str) -> CollectionResource:
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def load(cls, file_path: str):
        with open(file_path) as file:
            data = json.load(file)
        return cls.from_dict(data)


class Auth(CollectionResource):
    type: str | None = None  # apikey, awsv4, basic, bearer, digest, edgegrid, hawk, noauth, oauth1, oauth2, ntlm
    noauth: None = None
    apikey: list[AuthAttribute] | None = None
    awsv4: list[AuthAttribute] | None = None
    basic: list[AuthAttribute] | None = None
    bearer: list[AuthAttribute] | None = None
    digest: list[AuthAttribute] | None = None
    edgegrid: list[AuthAttribute] | None = None
    hawk: list[AuthAttribute] | None = None
    ntlm: list[AuthAttribute] | None = None
    oauth1: list[AuthAttribute] | None = None
    oauth2: list[AuthAttribute] | None = None


class AuthAttribute(CollectionResource):
    type: str | None = None
    key: str | None = None
    value: str | None = None


class Body(CollectionResource):
    mode: str | None = None  # raw, urlencoded, formdata, file, graphql
    raw: str | None = None
    graphql: object | None = None
    urlencoded: list[BodyUrlEncoded] | None = None
    formdata: list[BodyFormData] | None = None
    file: BodyFile | None = None
    options: object | None = None
    disabled: bool | None = None


class BodyFile(CollectionResource):
    src: str | None = None
    content: str | None = None


class BodyFormData(CollectionResource):
    key: str | None = None
    value: str | None = None  # for type=text
    src: list[str] | str | None = None  # for type=file
    disabled: bool | None = None
    type: str | None = None  # test | file
    contentType: str | None = None
    description: Description | str | None = None


class BodyUrlEncoded(CollectionResource):
    key: str | None = None
    value: str | None = None
    disabled: bool | None = None
    description: Description | str | None = None


class Certificate(CollectionResource):
    name: str | None = None
    matches: list[str] | None = None
    key: CertificateSrc | None = None
    cert: CertificateSrc | None = None
    passphrase: str | None = None


class CertificateSrc(CollectionResource):
    src: str | None = None


class Collection(CollectionResource):
    info: Info | None = None
    item: list[Item | ItemGroup] = Field(default_factory=list)
    event: list[Event] | None = None
    variable: list[Variable] | None = None
    auth: Auth | None = None
    protocolProfileBehavior: object | None = None
    postman_id: str | None = Field(alias="_postman_id", default=None)

    def model_post_init(self, __context):
        if not self.info:
            self.info = Info()

    @field_validator("item", mode="before")
    @classmethod
    def determine_item_type(cls, value):
        """Callable discriminator for a list of Foo and Bar"""
        if not isinstance(value, list):
            raise ValueError("'item' must be a list")
        parsed_items = []
        for item in value:
            if isinstance(item, dict):
                if "request" in item:
                    parsed_items.append(Item(**item))
                elif "item" in item:
                    parsed_items.append(ItemGroup(**item))
                else:
                    raise ValueError(f"Invalid object: {item} must contain 'request' for Item or 'item' for ItemGroup")
            else:
                raise ValueError(f"Invalid format: {item} must be a dictionary")
        return parsed_items


class Cookie(CollectionResource):
    domain: str | None = None
    path: str | None = None
    expires: str | None = None
    maxAge: str | None = None
    hostOnly: bool | None = False
    httpOnly: bool | None = False
    name: str | None = None
    secure: bool | None = False
    session: bool | None = False
    value: str | None = None
    extensions: list[Any] | None = None


class Description(CollectionResource):
    content: str | None = None
    type: str | None = None
    version: Version | str | None = None


class Event(CollectionResource):
    listen: str | None = None
    id: str | None = None
    script: Script | None = None
    type: bool | None = None


class Header(CollectionResource):
    key: str | None = None
    value: str | None = None
    disabled: bool | None = None
    description: Description | str | None = None


class Info(CollectionResource):
    # schema_field is aliased to schema to prevent naming conflict with Pydantic BaseModel
    name: str | None = None
    schema_: str = Field(alias="schema", default="https://schema.getpostman.com/json/collection/v2.1.0/collection.json")
    postman_id: str | None = Field(alias="_postman_id", default=None)
    exporter_id: str | None = Field(alias="_exporter_id", default=None)  # EXPORTED BUT NOT IN JSON SCHEMA
    collection_link: str | None = Field(alias="_collection_link", default=None)  # EXPORTED BUT NOT IN JSON SCHEMA
    description: Description | str | None = None
    version: Version | str | None = None


class Item(CollectionResource):
    request: Request | None = None
    id: str | None = None
    name: str | None = None
    description: Description | str | None = None
    variable: list[Variable] | None = None
    event: list[Event] | None = None
    response: list[Response] | None = None
    protocolProfileBehavior: object | None = None

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

    def create_request(self, url, method="GET"):
        request = Request()
        request.method = method
        request.url = URL()
        url_components = urllib.parse.urlparse(url)
        request.url.protocol = url_components.scheme
        request.url.host = url_components.hostname
        if url_components.port:
            request.url.port = url_components.port
        if len(url_components.path) > 1:
            request.url.path = url_components.path.split("/")[1:]
        if url_components.fragment:
            request.url.hash = url_components.fragment
        self.request = request
        return self.request

    def add_test_script(self, script: str | None = None):
        """Add a 'test' event script to the item."""
        event = Event()
        event.listen = "test"
        event.script = Script()
        if script:
            lines = []
            for line in script.splitlines():
                line.replace('"', '"')
                lines.append(line)
            event.script.exec = lines
        self.add_event(event)
        return event


class ItemGroup(CollectionResource):  # item-group in JSON schema
    item: list[Item | ItemGroup] = Field(default_factory=list)
    name: str | None = None
    description: Description | str | None = None
    variable: list[Variable] | None = None
    event: list[Event] | None = None
    auth: Auth | None = None
    protocolProfileBehavior: object | None = None

    @field_validator("item", mode="before")
    @classmethod
    def determine_item_type(cls, value):
        """Callable discriminator for a list of Item and ItemGroup"""
        if not isinstance(value, list):
            raise ValueError("'item' must be a list")
        parsed_items = []
        for item in value:
            if isinstance(item, dict):
                if "request" in item:
                    parsed_items.append(Item(**item))
                elif "item" in item:
                    parsed_items.append(ItemGroup(**item))
                else:
                    raise ValueError(f"Invalid object: {item} must contain 'request' for Item or 'item' for ItemGroup")
            else:
                raise ValueError(f"Invalid format: {item} must be a dictionary")
        return parsed_items


class ProxyConfig(CollectionResource):  # proxy-config in JSON schema
    match: str | None = None
    host: str | None = None
    port: int | None = None
    tunnel: bool | None = False
    disabled: bool | None = None


class ProtocolProfileBehavior(CollectionResource):  # proxy-profile-behavior in JSON schema
    # Object with no properties in JSON schema
    pass


class QueryParam(CollectionResource):
    key: str | None = None
    value: str | None = None
    disabled: bool | None = None
    description: Description | str | None = None


class Request(CollectionResource):
    url: URL | str | None = None
    auth: Auth | None = None
    proxy: ProxyConfig | None = None
    certificate: Certificate | None = None
    method: str | None = None  # GET,PUT,POST,DELETE,PATCH,HEAD,OPTIONS,PROPFIND,VIEW or custom value
    description: Description | str | None = None
    header: list[Header] | str | None = None
    body: Body | None = None

    def add_header(self, key, value, description=None):
        if not isinstance(self.header, list):
            self.header = []
        self.header.append(Header(key=key, value=value, description=description))


class Response(CollectionResource):
    id: str | None = None
    name: str | None = None  # EXPORTED BUT NOT IN JSON SCHEMA
    originalRequest: Request | None = None
    reponseTime: str | int | None = None
    timings: object | None = None
    header: list[Header] | str | None = None
    cookie: list[Cookie] | None = None
    body: str | None = None
    status: str | None = None
    code: int | None = None
    _postman_previewlanguage: str | None = None


class Script(CollectionResource):
    id: str | None = None
    type: str | None = None
    exec: list[str] | str | None = None
    src: URL | str | None = None
    name: str | None = None


class URL(CollectionResource):
    raw: str | None = None
    protocol: str | None = None
    host: str | list[str] | None = None
    path: str | list[str] | None = None
    port: str | None = None
    query: list[QueryParam] | None = None
    hash: str | None = None
    variable: list[Variable] | None = None

    """
    Add a query parameter to this URL, initializing the query array if needed.
    """

    def add_query_param(self, param):
        if not self.query:
            self.query = []
        self.query.append(param)

    """
    Add a variable to this URL, initializing the query array if needed.
    """

    def add_variable(self, variable):
        if not self.variable:
            self.variable = []
        self.variable.append(variable)

    """
    Helper function to create and add a query parameter
    """

    def create_query_parameter(
        self, key: str, value: str | None = None, description: str | None = None, disabled: bool | None = False
    ):
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

    """
    Helper function to create and add a variable
    """

    def create_variable(self, key: str, value: str | None = None, description: str | None = None):
        variable = Variable()
        variable.key = key
        if value:
            variable.value = value
        if description:
            variable.description = description
        self.add_variable(variable)
        return variable


class Variable(CollectionResource):
    id: str | None = None
    key: str | None = None
    value: Any | None = None
    type: str | None = None  # string, boolean, any, number
    name: str | None = None
    description: Description | str | None = None
    system: bool | None = None
    disabled: bool | None = None


class Version(CollectionResource):
    major: int = 0
    minor: int = 0
    patch: int = 0
    identifier: str | None = None
    meta: Any | None = None
