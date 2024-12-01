# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# for more information, see https://github.com/Temps233/pynarist/blob/master/NOTICE.txt

from inspect import get_annotations

from pynarist._errors import UsageError


def getClassFields(cls: type):
    fields = get_annotations(cls)
    for name, dtype in fields.items():
        if hasattr(cls, name):
            raise UsageError(
                "Initializations of field {} " "in class {} is not allowed".format(
                    name, cls.__name__
                )
            )
    return fields
