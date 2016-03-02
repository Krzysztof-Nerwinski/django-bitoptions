from django.db.models import IntegerField
from django.utils.translation import ugettext_lazy as _

from .lookups import BitwiseAnd
from .utils import BitOptions
from .widgets import BinaryWidget


class SimpleBitOptionsField(IntegerField):
    description = _('Bit options')

    def __init__(self, options=(), *args, **kwargs):
        if isinstance(options, BitOptions):
            self.options = options
        else:
            self.options = BitOptions(options)
        _len = len(self.options)
        if _len < 16:
            self._internal_type = 'PositiveSmallIntegerField'
        elif _len < 32:
            self._internal_type = 'PositiveIntegerField'
        elif _len < 64:
            self._internal_type = 'BigIntegerField'
        else:
            raise ValueError('Options list is longer than 63 items.')
        kwargs['default'] = kwargs.get('default', self.options.max)
        super(SimpleBitOptionsField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return self._internal_type

    def formfield(self, **kwargs):
        defaults = {'min_value': 0, 'max_value': self.options.max}
        defaults.update(kwargs)
        defaults['widget'] = BinaryWidget(choices=self.options)
        return super(SimpleBitOptionsField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(SimpleBitOptionsField,
                                         self).deconstruct()
        if kwargs['default'] == self.options.max:
            del kwargs['default']
        kwargs['options'] = self.options.flags
        return name, path, args, kwargs


class BitOptionsField(SimpleBitOptionsField):
    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def to_python(self, value):
        if value is None:
            return value
        value = super(BitOptionsField, self).to_python(value)
        return BitOptions(self.options.flags, value)

    def get_prep_value(self, value):
        if isinstance(value, BitOptions):
            return value.value
        return value

    def get_prep_lookup(self, lookup_type, value):
        value = self.get_prep_value(value)
        return super(BitOptionsField, self).get_prep_lookup(lookup_type, value)


SimpleBitOptionsField.register_lookup(BitwiseAnd)
