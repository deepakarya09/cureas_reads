from marshmallow import Schema, fields, ValidationError, validates
from marshmallow.validate import Length

from app.main.config import MIN_DEC_LENGTH, MIN_TAG_LENGTH, MIN_TITLE_LENGTH
from app.main.models.config_variables import ConfigVariables

