# from sqlalchemy import create_engine
# from twitter.utils.postgres_utils import get_connect_str

# class MetaSingleton(type):
#
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             # now the type's __call__() is only executed if cls is not in cls._instances
#             # This way we prevent new objects from being created if one exists
#             #when the constructor of classes deriving from MetaSingleton are created
#             cls._instances[cls] = super().__call__(*args, **kwargs)
#
#         return cls._instances[cls]
#
#
# class Connector(metaclass=MetaSingleton):
#
#     _connections = []
#
#     def __init__(self):
#         pass

# _connections = []
#
# def get_connection():
#     if _connections:
#         return _connections[0]
#     else:
#         connection = create_engine(get_connect_str()).connect()
#         _connections.append(connection)
#         return connection
