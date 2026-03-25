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

import inspect
import json
import logging
import re
import sys
import urllib
from dataclasses import asdict, dataclass, field, fields
from typing import Any


#
# HELPERS
#
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TypeDefinition:
    """ Represents a dataclass field type definition.
    Used by the deserializer when loading from JSON files.
    """
    def __init__(self, type_name, children=None, definition=None):
        self.type_name = type_name
        self.children = children if children is not None else []
        self.definition = definition
        self.type_category = self.determine_type_category()
        if self.type_category == "class":
            # get the class itself (needed by deserializer)
            # we assume at this point all classes belong to this module
            self.cls = getattr(sys.modules[__name__], self.type_name)
            # collect the dataclass fields
            if self.cls:
                self.fieldtypes = {f.name: f.type for f in fields(self.cls)}

    def determine_type_category(self):
        if self.type_name == 'list':
            return 'list'
        elif self.type_name == 'dict':
            return 'dict'
        elif self.type_name == 'union' or '|' in self.type_name:
            return 'union'
        elif self.type_name == 'Any': # this will force to return the value as is
            return 'primitive'
        elif self.type_name.lower() in {'int', 'float', 'str', 'bool', 'any', 'none', 'nonetype'}:
            return 'primitive'
        elif self.type_name.isidentifier() and not self.children:
            return 'class'
        else:
            return 'unknown'

    def __repr__(self):
        value = ""
        if self.definition:
            value += f"{self.definition}->"
        value += f"{self.type_name}"
        if self.children:
            value = f"({', '.join(repr(child) for child in self.children)}) [{self.definition}]"
        if self.type_category == "class":
            if self.fieldtypes:
                value += f"\n   {self.fieldtypes}"
        return value

def parse_type_definition(definition):
    """Parses a field type definition string into a TypeDefinition object.
    Used by the deserializer.
    """
    def split_top_level_union_types(def_str: str) -> list[str]:
        parts = []
        current = []
        depth = 0
        for char in def_str:
            if char == '[':
                depth += 1
                current.append(char)
            elif char == ']':
                depth -= 1
                current.append(char)
            elif char == '|' and depth == 0:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        parts.append(''.join(current).strip())
        return parts

    def parse_inner(def_str):
        def_str = def_str.strip()
        top_level_union_types = split_top_level_union_types(def_str)
        if len(top_level_union_types) > 1:
            return parse_union(def_str)
        elif def_str.startswith('list[') and def_str.endswith(']'):
            return parse_list(def_str)
        elif def_str.startswith('dict[') and def_str.endswith(']'):
            return parse_dict(def_str)
        else:
            return TypeDefinition(def_str.strip(), definition=def_str)

    def parse_list(def_str):
        """ Parse a list type definition string into a TypeDefinition object.
        Examples:
        list['Cookie']
        """
        if def_str.strip() == 'list':
            return TypeDefinition('list')
        match = re.match(r'list\[(.*)\]', def_str.strip())
        if match:
            inner_type = match.group(1)
            return TypeDefinition('list', [parse_inner(inner_type)], definition=def_str)
        else:
            raise ValueError(f"Invalid list type definition: {def_str}")

    def parse_dict(def_str):
        """ Parse a dict type definition string into a TypeDefinition object.
        Examples: No use case at this time
        """
        match = re.match(r'dict\[(.*)\]', def_str.strip())
        if match:
            key_value_types = match.group(1).split(',')
            if len(key_value_types) == 2:
                key_type = key_value_types[0].strip()
                value_type = key_value_types[1].strip()
                return TypeDefinition('dict', [parse_inner(key_type), parse_inner(value_type)], definition=def_str)
            else:
                raise ValueError(f"Invalid dict type definition: {def_str}")
        else:
            raise ValueError(f"Invalid dict type definition: {def_str}")

    def parse_union(def_str):
        """ Parse a union type definition string into a TypeDefinition object.
        Examples:
        'Description' | str
        'Version' | str
        list['Header'] | str
        list[str] | str
        list['Item'|'ItemGroup']
        list[str] | str
        dict[str,Foo] | Bar
        """
        types = split_top_level_union_types(def_str)
        return TypeDefinition('union', [parse_inner(t) for t in types])

    # Remove class definition surrouding quotes if exists
    # This happens when using deferred class declaration
     #like foo: 'Bar' (instead of Foo: Bar)
    definition = definition.replace("'","")
    # Recursively parse the type definition
    return parse_inner(definition)


def select_type_definition_from_data(union_type_definition, data):
    """Determines which type definition to use based on the data.
    Necessary when a field has allows for multiple types (union in Python or OneOf in JSON schema)
    """
    logging.debug(bcolors.OKGREEN)
    # get data type
    data_type = type(data).__name__
    logging.debug(f"data type: {data_type}")
    # if data is a dictionary, collect the keys (fields)
    if isinstance(data, dict):
        data_fields = set(data.keys())
        logging.debug(f"data dict fields: {data_fields}")

    selected_type = None
    # loop over union definitions
    for type_definition in union_type_definition.children:
        logging.debug(f"{type_definition}")
        if data is None and type_definition.type_name.lower() in {"none", "nonetype"}:
            logging.debug("none matched!")
            selected_type = type_definition
            break
        # data is primitive type
        if data_type in ["str", "int", "float", "bool", "NoneType"]:
            logging.debug("str_data_type")
            if type_definition.type_name == data_type:
                # matched
                logging.debug("primitive matched!")
                selected_type = type_definition
                break # we're done
        # dictionary type
        elif isinstance(data, dict):
            # compare keys/fields
            if type_definition.type_category == 'class':
                logging.debug(f"child fields: {type_definition.fieldtypes.keys()}")
                if data_fields.issubset(type_definition.fieldtypes.keys()):
                    # matched
                    logging.debug("dict matched!")
                    selected_type = type_definition
                    break # we're done
        else:
            logging.error(f"Unknown data type {data_type} in select_type_definition_from_data")
    # make the final choice
    if not selected_type:
        logging.warning(f"Warning: No type definition found for {data_type}. Using first available option...")
        selected_type = union_type_definition.children[0]
    logging.debug(bcolors.ENDC)
    return selected_type


#
# DATA CLASSES
#

class CollectionResource:
    """Base class for all Postman collection resource.
    """
    #
    # SERIALIZER
    #
    def asdict(self):
        return asdict(self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None})

    def toJSON(self, indent=None):
        return json.dumps(self.asdict(),indent=indent)

    def save(self, filepath, indent=4, format="json"):
        if format == "json":
            with open(filepath, 'w') as f:
                json.dump(self.asdict(), f, indent=indent)
        else:
            raise ValueError(f"Unsupported format: {format}")


    #
    # DESERIALIZER
    #
    @classmethod
    def from_dict(cls, data: dict) -> Any:
        """Deserializes from a dictionary.
        """

        # Define an inner function that recursively handles the actual deserialization process
        def from_dict_inner(definition, data):
            """
            Recursively deserializes nested elements from a dictionary

            The definition can be:
             - a string value coming from the dataclass field definitions
             - a readily parsed TypeDefinition
             - a dataclass object or name

            The data holds the object data as a dictionary or primitive value,
            typically dictionary coming from a JSON file
            """
            logging.debug(f"DESERIALIZING {definition}")

            # INIT
            # if definition is a class, use its name instead
            if inspect.isclass(definition):
                definition = definition.__name__
            # if definition is already the right type, not need to further process
            if isinstance(definition, TypeDefinition):
                type_definition = definition
            elif isinstance(definition, str):
                # if definition is a string, parse it
                type_definition = parse_type_definition(definition)
            else:
                raise ValueError(f"Invalid definition: {definition}")

            # DISAMBIGUATE UNION
            if type_definition.type_category == "union":
                # infer the type based on the content of the data
                type_definition = select_type_definition_from_data(type_definition, data)

            # PROCESS DATACLASS TYPE
            if type_definition.type_category == "class":
                logging.debug(f"{bcolors.OKBLUE}-- DATACLASS --{bcolors.ENDC}")
                # Retrieve the class
                if hasattr(sys.modules[__name__], type_definition.type_name):
                    cls = getattr(sys.modules[__name__], type_definition.type_name)
                    # Retrieve the field types
                    fieldtypes = {f.name: f.type for f in fields(cls)}
                    # Retrieve the field values
                    field_values = {}
                    for f in fieldtypes:
                        if f in data:
                            # If the field is in the data, recursively call from_dict_inner to deserialize it
                            field_values[f] = from_dict_inner(fieldtypes[f], data[f])
                        else:
                            # If the field is not in the data, set it to None
                            # field_values[f] = None
                            pass

                    logging.debug(f"Deserialized field values:{field_values}")

                    # Report fields in dict but not in dataclass
                    if isinstance(data, dict):
                        missing_fields = [f for f in data if f not in fieldtypes]
                        if missing_fields:
                            logging.error(f"Missing fields: {missing_fields} for\n{definition}")

                    # Step 3: Instantiate the dataclass
                    # Use the dictionary of field values to create an instance of the dataclass
                    instance = cls(**field_values)
                    logging.debug(f"{bcolors.OKBLUE}--> RETURN DATACLASS {instance}{bcolors.ENDC}")
                    return instance
                else:
                    raise ValueError(f"Definition {definition} not found")

            # PROCESS LIST TYPE
            elif type_definition.type_category == "list":
                logging.debug(f"{bcolors.OKBLUE}-- LIST --{bcolors.ENDC}")
                list_type_definition = type_definition.children[0]
                # Recursively process each item in the list
                values = []
                for item in data:
                    values.append(from_dict_inner(list_type_definition, item))
                logging.debug(f"{bcolors.OKBLUE}--> RETURN LIST {values}{bcolors.ENDC}")
                return values

            # PROCESS DICTIONARY TYPE
            # note: we do not have dict in the current model
            elif type_definition.type_category== "dict":
                # TODO
                logging.debug(f"{bcolors.OKBLUE}-- DICT --{values}{bcolors.ENDC}")
                key_type, value_type = cls.__args__
                # Recursively process each item in the dict
                dct = {from_dict_inner(key_type, k): from_dict_inner(value_type, v) for k, v in data.items()}
                logging.debug(f"{bcolors.OKBLUE}--> RETURN DICT {dict}{bcolors.ENDC}")
                return dct

            # PROCESS PRIMITIVE TYPE
            elif type_definition.type_category == "primitive":
                logging.debug(f"{bcolors.OKBLUE}-- PRIMITIVE --{bcolors.ENDC}")
                # If the type is not a dataclass or a list, return the data directly
                logging.debug(f"{bcolors.OKBLUE}--> RETURN PRIMITIVE:{data}{bcolors.ENDC}")
                return data
            else:
                logging.error(f"Unsupported type definition {type_definition} ({type_definition.type_category})")

        # Call the inner function with the initial class and data to start the deserialization process
        return from_dict_inner(cls.__name__, data)

    @classmethod
    def from_json(cls, json_str: str) -> Collection:
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def load(cls, file_path: str):
        with open(file_path) as file:
            data = json.load(file)
        return cls.from_dict(data)

@dataclass
class Auth(CollectionResource):
    type: str | None = None # apikey, awsv4, basic, bearer, digest, edgegrid, hawk, noauth, oauth1, oauth2, ntlm
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

@dataclass
class AuthAttribute(CollectionResource):
    key: str | None = None
    value: str | None = None
    type: str | None = None

@dataclass
class Body(CollectionResource):
    mode: str | None = None # raw, urlencoded, formdata, file, graphql
    raw: str | None = None
    graphql: object | None = None
    urlencoded: list[BodyUrlEncoded] | None = None
    formdata: list[BodyFormData] | None = None
    file: BodyFile | None = None
    options: object | None = None
    disabled: bool | None = None

@dataclass
class BodyFile(CollectionResource):
    src: str | None = None
    content: str | None = None

@dataclass
class BodyFormData(CollectionResource):
    key: str | None = None
    value: str | None = None # for type=text
    src: list[str] | str | None = None # for type=file
    disabled: bool | None = None
    type: str | None = None # test | file
    contentType: str | None = None
    description: Description | str | None = None

@dataclass
class BodyUrlEncoded(CollectionResource):
    key: str | None = None
    value: str | None = None
    disabled: bool | None = None
    description: Description | str | None = None

@dataclass
class Certificate(CollectionResource):
    name: str | None = None
    matches: list[str] | None = None
    key: CertificateSrc | None = None
    cert: CertificateSrc | None = None
    passphrase: str | None = None

@dataclass
class CertificateSrc(CollectionResource):
    src: str | None = None

@dataclass
class Collection(CollectionResource):
    info: Info | None = None
    item: list[Item | ItemGroup] = field(default_factory=list)
    event: list[Event] | None = None
    variable: list[Variable] | None = None
    auth: Auth | None = None
    protocolProfileBehavior: object | None = None
    _postman_id: str | None = None

    def __post_init__(self):
        if not self.info:
            self.info = Info()

@dataclass
class Cookie(CollectionResource):
    domain: str | None = None
    expires: str | None = None
    maxAge: str | None = None
    hostOnly: bool = False
    httpOnly: bool = False
    name: str | None = None
    path: str | None = None
    secure: bool = False
    session: bool = False
    value: str | None = None
    extensions: list[Any] | None = None

@dataclass
class Description(CollectionResource):
    content: str | None = None
    type: str | None = None
    version: Version | str | None = None

@dataclass
class Event(CollectionResource):
    id: str | None = None
    listen: str | None = None
    script: Script | None = None
    type: bool | None = None

@dataclass
class Header(CollectionResource):
    key: str | None = None
    value: str | None = None
    disabled: bool | None = None
    description: Description | str | None = None

@dataclass
class Info(CollectionResource):
    name: str | None = None
    _postman_id: str | None = None
    _exporter_id: str | None = None # EXPORTED BUT NOT IN JSON SCHEMA
    _collection_link: str | None = None # EXPORTED BUT NOT IN JSON SCHEMA
    description: Description | str | None = None
    version: Version | str | None = None
    schema: str = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"

@dataclass
class Item(CollectionResource):
    id: str | None = None
    name: str | None = None
    description: Description | str | None = None
    variable: list[Variable] | None = None
    event: list[Event] | None = None
    request: Request | None = None
    response: list[Response] | None = None
    protocolProfileBehavior: object | None = None

    def __post_init__(self):
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


@dataclass
class ItemGroup(CollectionResource): # item-group in JSON schema
    name: str | None = None
    description: Description | str | None = None
    variable: list[Variable] | None = None
    item: list[Item | ItemGroup] = field(default_factory=list)
    event: list[Event] | None = None
    auth: Auth | None = None
    protocolProfileBehavior: object | None = None

@dataclass
class ProxyConfig(CollectionResource): # proxy-config in JSON schema
    match: str | None = None
    host: str | None = None
    port: int | None = None
    tunnel: bool = False
    disabled: bool | None = None

@dataclass
class ProtocolProfileBehavior(CollectionResource): # proxy-profile-behavior in JSON schema
    # Object with no properties in JSON schema
    pass
@dataclass
class QueryParam(CollectionResource):
    key: str | None = None
    value: str | None = None
    disabled: bool | None = None
    description: Description | str | None = None

@dataclass
class Request(CollectionResource):
    url: URL | str | None = None
    auth: Auth | None = None
    proxy: ProxyConfig | None = None
    certificate: Certificate | None = None
    method: str | None = None # GET,PUT,POST,DELETE,PATCH,HEAD,OPTIONS,PROPFIND,VIEW or custom value
    description: Description | str | None = None
    header: list[Header] | str | None = None
    body: Body | None = None

    def add_header(self, key, value, description=None):
        if not isinstance(self.header, list):
            self.header = []
        self.header.append(Header(key=key, value=value, description=description))

@dataclass
class Response(CollectionResource):
    id: str | None = None
    name: str | None = None # EXPORTED BUT NOT IN JSON SCHEMA
    originalRequest: Request | None = None
    responseTime: str | int | None = None
    timings: object | None = None
    header: list[Header] | str | None = None
    cookie: list[Cookie] | None = None
    body: str | None = None
    status: str | None = None
    code: int | None = None
    _postman_previewlanguage: str | None = None


@dataclass
class Script(CollectionResource):
    id: str | None = None
    type: str | None = None
    exec: list[str] | str | None = None
    src: URL | str | None = None
    name: str | None = None

@dataclass
class URL(CollectionResource):
    raw: str | None = None
    protocol: str | None = None
    host: str | list[str] | None = None
    path: str | list[str] | None = None
    port: str | int | None = None
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

@dataclass
class Variable(CollectionResource):
    id: str | None = None
    key: str | None = None
    value: Any | None = None
    type: str | None = None # string, boolean, any, number
    name: str | None = None
    description: Description | str | None = None
    system: bool | None = None
    disabled: bool | None = None

@dataclass
class Version(CollectionResource):
    major: int = 0
    minor: int = 0
    patch: int = 0
    identifier: str | None = None
    meta: Any | None = None

