Postman Collection
==================

Importing or exporting Postman Collections is based on the `Postman Collection schema <https://schema.postman.com/>`_ JSON specification.
This package includes Python classes that can be used to programmatically interact with this model and serialize/deserialize to JSON.

The initial implementation used traditional Python `Data Classes <https://docs.python.org/3/library/dataclasses.html>`_.

The package is being rewritten using `Pydantic <https://docs.pydantic.dev/latest/>`_ to strengthen features/validation and facilitate integration with other packages and frameworks, particularly LangChain.


Create a collection from scratch
--------------------------------

.. code-block:: python

   from dartfx.postmanapi import postman_collection as pc

   # Collection
   collection = pc.Collection()
   print(collection)
   collection.info.name="Hello World"
   # Item
   item = pc.Item(name="Hello World")
   collection.item.append(item)
   # Request
   request = pc.Request(method="POST", url="https://postman-echo.com/post")
   request.body = pc.Body(mode="raw", raw='{"message": "Hello, World!"}')
   request.add_header("Content-Type", "application/json")
   item.request = request
   # save
   filename = "hello_world.dc.json"
   collection.save(filename)


Loading an exported collection 
------------------------------

.. code-block:: python

   from dartfx.postmanapi import postman_collection as pc

   filename = "exported_foo.json"
   # deserialize
   collection = pc.Collection.load("foo.json")
   # ...do something...
   # save (or import/update via PostmanAPI)
   collection.save("bar.json")

