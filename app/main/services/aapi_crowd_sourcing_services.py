import calendar
import time
import uuid
from http import HTTPStatus

from sqlalchemy import or_
from werkzeug.exceptions import BadRequest

from app.main import config
from app.main import db
from app.main.models.submissions import Submission
from app.main.models.submitted_articles import SubmittedArticle


def get_submission_by_id(id):
    try:
        uuid.UUID(id)
    except Exception as e:
        config.logging.warning(f"api: get_submission_by_id: Invalid Submission {id}")
        raise BadRequest(f"This submission id not valid - {id}.")

    submission = Submission.query.filter_by(id=id).first()
    if not submission:
        raise BadRequest("Submission not in database.")
    return submission, HTTPStatus.OK.value


def get_all_submissions(page, limit, searchKey):

    if searchKey:
        search = "%{}%".format(searchKey)
        paginated_data = Submission.query.order_by(Submission.created_at.desc()).filter(or_(Submission.worker_id.ilike(search), Submission.confirmation_code.ilike(search))).paginate(
            page=page, per_page=limit)
        objects = paginated_data.items
    else:
        paginated_data = Submission.query.order_by(
            Submission.created_at.desc()).paginate(page=page, per_page=limit)
        objects = paginated_data.items

    return {"items": objects,
            "page": paginated_data.page,
            "per_page": paginated_data.per_page,
            "total": paginated_data.total,
            "total_pages": [page for page in paginated_data.iter_pages()],
            }, HTTPStatus.OK.value


def update_worker(data, submission_id):
    try:
        uuid.UUID(submission_id)
    except Exception:
        raise BadRequest("This submission id not valid.")

    update = Submission.query.filter_by(id=submission_id).first()
    if not update.confirmation_code:
        raise BadRequest("Payment Status can not be updated for record without confirmation code")

    if not update:
        raise BadRequest("This submission id not present.")

    if not Submission.query.filter_by(worker_id=data['workerId'], id=submission_id).first():
        raise BadRequest("Not a valid workerId.")

    try:
        update.payment_status = data['paymentStatus']
        update.payment_status_update_at = calendar.timegm(time.gmtime()) if data['paymentStatus'] else None
        update.modified_at = calendar.timegm(time.gmtime())
        db.session.commit()
    except Exception as e:
        raise BadRequest(f"Failed to update.{e}")
    return update


def get_extension_submitted(page, limit, searchKey):
    if searchKey:
        search = "%{}%".format(searchKey)
        paginated_data = SubmittedArticle.query.order_by(SubmittedArticle.created_at.desc()).filter(
            SubmittedArticle.submission_id == None).filter(or_(SubmittedArticle.title.ilike(search), SubmittedArticle.description.ilike(search), SubmittedArticle.city.ilike(search))).paginate(
            page=page, per_page=limit)
        objects = paginated_data.items
    else:
        paginated_data = SubmittedArticle.query.order_by(SubmittedArticle.created_at.desc()).filter_by(
            submission_id=None).paginate(
            page=page, per_page=limit)
        objects = paginated_data.items

    return {"items": objects,
            "page": paginated_data.page,
            "per_page": paginated_data.per_page,
            "total": paginated_data.total,

            "total_pages": [page for page in paginated_data.iter_pages()],
            }, HTTPStatus.OK.value
