
# -*- coding: utf-8 -*-
"""
    Chapter 1.1
    ~~~~~~~~~~~~~~
    Class assignment.
    :By Spencer Post.
    :license: BSD, see LICENSE for more details.
"""

import numpy
from datetime import datetime


class SessionMixin(object):
    """Expands a basic dictionary with an accessors that are expected
    by Flask extensions and users for the session.
    """

    def _get_permanent(self):
        return self.get('_permanent', False)

    def _set_permanent(self, value):
        self['_permanent'] = bool(value)

    #: this reflects the ``'_permanent'`` key in the dict.
    permanent = property(_get_permanent, _set_permanent)
    del _get_permanent, _set_permanent

    #: some session backends can tell you if a session is new, but that is
    #: not necessarily guaranteed.  Use with caution.  The default mixin
    #: implementation just hardcodes ``False`` in.
    new = False

    #: for some backends this will always be ``True``, but some backends will
    #: default this to false and detect changes in the dictionary for as
    #: long as changes do not happen on mutable structures in the session.
    #: The default mixin implementation just hardcodes ``True`` in.
    modified = True


def _tag(value):
    if isinstance(value, tuple):
        return {' t': [_tag(x) for x in value]}
    elif isinstance(value, uuid.UUID):
        return {' u': value.hex}
    elif isinstance(value, bytes):
        return {' b': b64encode(value).decode('ascii')}
    elif callable(getattr(value, '__html__', None)):
        return {' m': text_type(value.__html__())}
    elif isinstance(value, list):
        return [_tag(x) for x in value]
    elif isinstance(value, datetime):
        return {' d': http_date(value)}
    elif isinstance(value, dict):
        return dict((k, _tag(v)) for k, v in iteritems(value))
    elif isinstance(value, str):
        try:
            return text_type(value)
        except UnicodeError:
            from flask.debughelpers import UnexpectedUnicodeError
            raise UnexpectedUnicodeError(u'A byte string with '
                    u'non-ASCII data was passed to the session system '
                    u'which can only store unicode strings.  Consider '
                    u'base64 encoding your string (String was %r)' % value)
    return value
