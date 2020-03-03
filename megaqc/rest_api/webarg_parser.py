from querystring_parser import parser as qsp
from webargs import core
from webargs.flaskparser import FlaskParser


class NestedQueryFlaskParser(FlaskParser):
    def parse_querystring(self, req, name, field):
        return core.get_value(qsp.parse(req.query_string), name, field)
        # return qsp.parse(req.query_string)[name]


parser = NestedQueryFlaskParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
error_handler = parser.error_handler
