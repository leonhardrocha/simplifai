# import abc
# import os
# import chromadb
# from dotenv import load_dotenv


# class VectorSearchClientInterface(metaclass=abc.ABCMeta):
#     """
#     An abstract class that defines the interface for a vector search client.
#     """
#     @classmethod
#     def __subclasshook__(cls, subclass):
#         """
#         A class method that checks if the given subclass is a subclass of the class it is defined on.
#         It does this by checking if the subclass has an attribute named 'get_retriever' and if it is callable.

#         :param cls: The class object.
#         :type cls: type
#         :param subclass: The subclass to check.
#         :type subclass: type
#         :return: True if the subclass is a subclass of the class it is defined on and has an a
#           ttribute named 'get_retriever'
#           and it is callable, False otherwise.
#         :rtype: bool
#         """
#         return (hasattr(subclass, 'get_retriever') and callable(subclass.get_retriever))


# class ChromaDBClient(VectorSearchClientInterface):
#     """ChromaDB concrete class for VectorSearchClient"""
#     def __init__(self, personal_access_token, **kwargs):
#         if personal_access_token is None:
#             personal_access_token = os.environ.get("CHROMA_SERVER_AUTH_TOKEN_TRANSPORT_HEADER")

#         self.chromadb_reader = ChromaDBReader(personal_access_token, **kwargs)

#     def get_retriever(self, vectordb_client: chromadb.Client, vector_search_schema: dict = None, token: str = None):
#         """
#         Returns a retriever object for the given vectordb_client.

#         Args:
#             vectordb_client (chromadb.PersistentClient): The client to interact with the vector database.
#             vector_search_schema (dict, optional): The schema for the vector search. Defaults to None.
#             token (str, optional): The token for authentication. Defaults to None.

#         Returns:
#             Retriever: The retriever object.
#         """
#         vectordb_client = self.chromadb_reader.get_vectordb_client()
#         return vectordb_client.


# class ChromaDBReader():
#     """
#     A class for interacting with the ChromaDB vector database.
#     """
#     def __init__(self, personal_access_token, disable_notice=True):
#         """
#         Initializes an instance of the class.

#         Args:
#             personal_access_token (str): The personal access token for authentication.
#             disable_notice (bool, optional): Whether to disable notice. Defaults to True.

#         Returns:
#             None
#         """
#         self.personal_access_token = personal_access_token
#         self.disable_notice = disable_notice

#     def get_vectordb_client(self) -> chromadb.Client:
#         """
#         Returns a client for the ChromaDB library.

#         This function loads the environment variables from the '.env.vectordb' file,
#         retrieves the 'STORAGE_PATH' environment variable, and sets the default value
#         to './storage'. It then creates the storage directory if it doesn't exist.
#         Finally, it initializes and returns a persistent client for the ChromaDB library.

#         Returns:
#             chromadb.PersistentClient: A persistent client for the ChromaDB library.
#         """
#         load_dotenv('.env.vectordb')

#         storage_path = os.getenv('STORAGE_PATH', './storage')
#         os.makedirs(storage_path, exist_ok=True)
#         vectordb_client = chromadb.PersistentClient(path=storage_path)
#         return vectordb_client

#     def get_or_create_collection(self, vectordb_client: chromadb.PersistentClient, name: str):
#         """
#         Returns a collection from the given `vectordb_client` if it exists, otherwise creates a
#            new collection with the given `name`.

#         Parameters:
#             vectordb_client (chromadb.PersistentClient): The client to interact with the vector database.
#             name (str): The name of the collection.

#         Returns:
#             chromadb.Collection: The collection with the given `name`.
#         """
#         vectordb_client = self.get_vectordb_client()
#         collection = vectordb_client.get_or_create_collection(name=name)
#         return collection

#     VectorSearchClientInterface.register()
