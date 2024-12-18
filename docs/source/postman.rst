Postman
=======

The Postman API package provides various classes to facilitate the interaction with the platform.

Postman API
-----------

The PostmanAPI class is at the foundation of the package and manages all interactions with the Postman API. 

It is used to:

- call low level or core methods
- instantiate higher level classes

To instantiate it, you will need a valid `Postman API <https://learning.postman.com/docs/developer/postman-api/authentication/>`_ key.

.. code-block:: python

   from dartfx.postmanapi import postman
   api = postman.PostmanApi(os.environ.get('POSTMAN_API_KEY'))

   user_profile = api.get_user_profile()
   print(user_profile)


Workspace Manager
-----------------

.. code-block:: python

   from dartfx.postmanapi import postman

   # create a workspace
   api = postman.PostmanApi(os.environ.get('POSTMAN_API_KEY'))
   id = api.create_workspace('test_workspace',"personal")

   # instantiate a workspace manager
   ws = postman.WorkspaceManager(get_api(), id)

   # get info
   print(ws.name)
   print(ws.description)
   global_vars = ws.global_variables

   # enumerate collections
   for collection in ws.collections
      print(collection.name)

   # create a collection
   c1 = ws.create_collection("The One")
   c2 = ws.create_collection("It Takes Two")
   c3 = ws.create_collection("Three of a Kind")

   # delete  workspace
   api.delete_workspace(id)


Collection Manager
------------------

TODO...