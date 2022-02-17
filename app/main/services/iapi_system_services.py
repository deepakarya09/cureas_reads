from werkzeug.exceptions import BadRequest

from app.main import db, config
from app.main.models.config_variables import ConfigVariables
from http import HTTPStatus
from werkzeug.exceptions import NotFound


def save_config_vars(data):
    save_con = ConfigVariables(
        key=data['key'],
        value=data['value'])
    db.session.add(save_con)
    db.session.commit()
    config.logging.warning(f"api: save config var: success")
    return save_con


def validation(data):
    if ConfigVariables.query.filter_by(key=data['key']).first():
        raise BadRequest("This key already present.")
    save_ob = save_config_vars(data)

    return save_ob, HTTPStatus.CREATED.value


def get_all_config_vars():
    return {"configVariables": ConfigVariables.query.all()}, HTTPStatus.OK.value


def update_config_var(key, data):
    try:
        config_var = ConfigVariables.query.filter_by(key=key).first()
        config_var.value = data['value']
        db.session.commit()
        return config_var, HTTPStatus.OK.value
    except Exception as e:
        config.logging.warning(f"api: update config var: config variable not exists:{e}")
        raise NotFound("config variable not exists.")


def delete_config_var(key):
    try:
        config_var = ConfigVariables.query.filter_by(key=key).first()
        db.session.delete(config_var)
        db.session.commit()
        return {"message": "Key deleted successfully."}, HTTPStatus.OK.value
    except Exception as e:
        config.logging.warning(f"api: delete config var: config variable not exists:{e}")
        raise NotFound("config variable not exists.")
