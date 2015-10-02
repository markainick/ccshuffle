#   COPYRIGHT (c) 2015 Kevin Haller <kevin.haller@outofbits.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
import json
from abc import abstractmethod
from django.core.serializers.json import DjangoJSONEncoder


class DeserializableException(Exception):
    """ This exception will be thrown, if the serialized representation can't be parsed correctly."""
    pass


class SerializableModel(object):
    """ This class represents json models that have the function 'serializable' that returns a serializable object.  """

    @abstractmethod
    def serialize(self):
        """
        Serializes this object so that it can be converted to JSON for example.

        :return:the serialized object.
        """
        raise NotImplementedError('The function serialize of %s' % self.__class__.__name__)

    @classmethod
    @abstractmethod
    def from_serialized(cls, obj):
        """
        Parses the serialized representation of the object of this class and returns a object of this class. Throws a
        DeserializableException, if the representation can not be pared.

        :param obj: the serialized representation of the object, which shall be parsed.
        :return: the object of this class.
        """
        raise NotImplementedError('The function from_serialized of %s' % cls.__class__.__name__)


class JSONModelEncoder(DjangoJSONEncoder):
    """  This class represents a json encoder for the models, which are instance of the ModelSerializable class."""

    def default(self, o):
        if o is None:
            return None
        elif isinstance(o, (str, int, float)):
            return str(o)
        elif isinstance(o, (dict, set)):
            return {key: self.default(o[key]) for key in o}
        elif isinstance(o, (list, tuple)):
            return [self.default(entry) for entry in o]
        elif isinstance(o, SerializableModel):
            # Serialize if the object is serializable.
            return self.default(o.serialize())
        else:
            return super(type(self), self).default(o)


class ResponseObject(object):
    """ Response object for the ajax requests of the dashboard """

    def __init__(self, status='success', error_msg='', result_obj=None):
        """
        Initializes the response object.

        :param status: success or fail.
        :param error_msg: the error message if the status is 'fail'.
        :param result_obj: the result object, which is json serializable.
        """
        self.response_dic = {
            'header': {'status': status, 'error_message': error_msg},
            'result': result_obj,
        }

    def result_object(self):
        """
        Returns the the same object passed through the constructor as result object.

        :return: the same object passed through the constructor.
        """
        return self.response_dic['result']

    def json(self, cls=None):
        """
        Returns the json dump of the result object.

        :param cls: optional the class for serializing the result object, otherwise the default serializer
                    JSONEncoder.
        :return: the json dump of the result object.
        """
        return json.dumps(self.response_dic, cls=cls)
