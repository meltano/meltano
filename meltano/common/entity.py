import io

from typing import Optional
from meltano.schema import DBType


class TransientAttribute:
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type

    def copy(self):
        return TransientAttribute(self.name, self.data_type)

    def __eq__(self, other):
        return self.name == other.name and \
          self.data_type == other.data_type

    def __repr__(self):
        return "{}: {}".format(self.name, self.data_type)


class Attribute:
    def __init__(self, alias,
                 input: Optional[TransientAttribute],
                 output: Optional[TransientAttribute],
                 db_type=DBType.String,
                 metadata={}):
        self.alias = alias
        self.input = input or TransientAttribute(alias, db_type)
        self.output = output or self.input.copy()
        self.metadata = metadata

    def __repr__(self):
        out = repr(self.input)
        if self.output != self.input:
            out += " as {}".format(self.output)

        return out

    @property
    def name(self):
        return self.output.name

    @property
    def data_type(self):
        return self.output.data_type


class Entity:
    def __init__(self, name, alias=None, attributes=[], metadata={}):
        self.name = name
        self.alias = alias or name.lower()
        self.attributes = attributes
        self.metadata = metadata

    def __repr__(self):
        out = io.StringIO()

        out.write("{} as {}:".format(self.name, self.alias))
        [out.write("\n\t{}".format(attr)) for attr in self.attributes]

        return out.getvalue()
