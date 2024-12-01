from inspect import get_annotations


def getClassFields(cls: type):
    fields = get_annotations(cls)
    for name, dtype in fields.items():
        if hasattr(cls, name):
            raise TypeError(
                "Initializations of field {} " "in class {} is not allowed".format(
                    name, cls.__name__
                )
            )
    return fields
