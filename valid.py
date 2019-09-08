import json
from markupsafe import Markup
from secrets import token_urlsafe

from enum import Enum, IntEnum


class CSRFTError(Exception):
    pass


class ValidationError:
    def __init__(self, field, message):
        self.field = field
        self.message = message

    def json(self):
        j = dict()
        if self.field:
            j['field'] = self.field
        if self.message:
            j['reason'] = self.message
        return j


class Validate:
    def __init__(self, request, require_csrft=True):
        if isinstance(request, dict):
            self.source = request
        else:
            contentType = request.headers.get("Content-Type")
            if contentType and contentType == "application/json":
                self.source = json.loads(request.data.decode('utf-8'))
            else:
                self.source = request.form
            self.request = request
        self.errors = []
        self.status = 400
        self._kwargs = {
            "valid": self
        }
        if require_csrft:
            self._csrft = self.source.get('_csrft')
            if self._csrft is None:
                raise CSRFTError()

    @property
    def ok(self):
        return len(self.errors) == 0

    @property
    def err(self):
        return not self.ok

    def summary(self, name=None):
        errors = [e.message for e in self.errors if e.field == name or name == '@all']
        if len(errors) == 0:
            return ''
        if name in (None, '@all'):
            return Markup(f'<div class="notification is-danger">{"<br>".join(errors)}</div>')
        else:
            return Markup("<br>".join(errors))

    @property
    def response(self):
        return {"errors": [e.json() for e in self.errors]}, self.status

    @property
    def kwargs(self):
        return self._kwargs

    def error(self, message, field=None, status=None):
        self.errors.append(ValidationError(field, message))
        if status:
            self.status = status
        return self.response

    def optional(self, name, default=None, cls=None):
        value = self.source.get(name)
        if value is None:
            value = default
        if value is not None:
            if cls and issubclass(cls, IntEnum):
                if not isinstance(value, int):
                    self.error('{} should be an int'.format(name), field=name)
                else:
                    value = cls(value)
            elif cls and issubclass(cls, Enum):
                if not isinstance(value, str):
                    self.error("{} should be an str".format(name), field=name)
                else:
                    if value not in (m[0] for m in cls.__members__.items()):
                        self.error("{} should be a valid {}".format(name, cls.__name__), field=name)
                    else:
                        value = cls(value)
            elif cls and not isinstance(value, cls):
                self.error('{} should be a {}'.format(name, cls.__name__), field=name)
        self._kwargs[name] = value
        return value

    def require(self, name, cls=None, friendly_name=None):
        value = self.optional(name, None, cls)
        if not friendly_name:
            friendly_name = name
        if not value:
            self.error(f'{friendly_name} is required', field=name)
        return value

    def expect(self, condition, message, field=None):
        if not condition:
            self.error(message, field)

    def csrft(self, session):
        if '__CSRFT' not in session:
            self.error("Cross-Site Token is missing")
            return False
        return True

    def copy(self, valid, field=None):
        for err in self.errors:
            valid.error(err.message, field + "." + err.field)

    def __contains__(self, value):
        return value in self.source

    def file(self, name):
        return self.request.files.get(name)


def HTML_CSRFT(session):
    if '__CSRFT' not in session:
        session['__CSRFT'] = token_urlsafe(32)
    return Markup(f"<input type='hidden' name='_csrft' value='{session['__CSRFT']}' />\n")


def Str_CSRFT(session):
    if '__CSRFT' not in session:
        session['__CSRFT'] = token_urlsafe(32)
    return str(session['__CSRFT'])
