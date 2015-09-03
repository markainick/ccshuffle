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
from django.db import models
from ccshuffle.serialize import SerializableModel, DeserializableException

from datetime import datetime


class CrawlingProcess(models.Model, SerializableModel):
    Service_Jamendo = 'Jamendo'
    Service_Soundcloud = 'Soundcloud'
    Service_CCMixter = 'CCMixter'
    Service_General = 'GENERAL'

    Status_Planned = 'Planned'
    Status_Running = 'Running'
    Status_Finished = 'Finished'
    Status_Failed = 'Failed'

    service = models.CharField(max_length=100, blank=False)
    execution_date = models.DateTimeField(blank=False, default=datetime.now)
    status = models.CharField(max_length=100, blank=False)
    exception = models.CharField(max_length=500, blank=True, null=True)

    def serialize(self):
        return {
            'service': self.service,
            'execution_date': self.execution_date,
            'status': self.status,
            'exception': self.exception,
        }

    @classmethod
    def from_serialized(cls, obj):
        if isinstance(obj, cls):
            return obj
        elif isinstance(obj, (dict, set)):
            try:
                execution_date = obj['execution_date']
                if isinstance(execution_date, str):
                    execution_date = datetime.strptime(obj['execution_date'], '%Y-%m-%dT%H:%M:%S')
                elif not isinstance(execution_date, datetime):
                    raise DeserializableException('The given release date can\'t be parsed.')
                return cls(service=obj['service'], execution_date=execution_date, status=obj['status'],
                           exception=obj['exception'])
            except KeyError as e:
                raise DeserializableException('The given serialized representation is corrupted.') from e
        else:
            raise DeserializableException(
                'The given object %s can\'t be parsed. It is no dictionary or set (%s).' % (repr(obj), type(obj)))

    def __str__(self):
        return '%s (%s - %s)' % (self.execution_date, self.service, self.status)
