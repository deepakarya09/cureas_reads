from flask_restplus import Namespace, fields


class ConfigVarsDto:
    api = Namespace('config_variables', description='config variables related operations')

    res_config = api.model("Config Variables", {
        "key": fields.String(description='key'),
        "value": fields.String(description='value'),
    })

    req_config_variable = api.model("Config Variables", {
        "key": fields.String(description='key'),
        "value": fields.String(description='value'),
    })

    res_all_config_variables = api.model('response of all config variables', {
        "configVariables": fields.List(fields.Nested(res_config)),
    })

    res_for_put = api.model("update config variable", {
        "key": fields.String(description='key'),
        "value": fields.String(description='value'),
    })
