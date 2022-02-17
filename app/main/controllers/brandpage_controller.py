from app.main.tokenvalidation.token_check import scope, token_required
from app.main.services.image_upload_services import upload_images_api
from flask import current_app as cur_app
from flask import request

from app.main.services.pages.brand_pages_service import duplicate_page, get_all_contents, get_all_system_pages, get_page, delete_page, \
    get_all_draft_or_published_pages, issue_template_before_save, save_publish_and_draft, preview_page, update_page_by_id
from app.main.utils.brand_pages_dto import BradPageDTO
from flask_restplus import Resource

api = BradPageDTO.api
_req_for_draft_publish = BradPageDTO.req_for_draft_publish
_res_page_by_id = BradPageDTO.res_page_by_id
_res_issue_template_before_save = BradPageDTO.res_issue_template_before_save
_res_for_draft_publish = BradPageDTO.res_for_draft_publish
_req_for_draft_publish_update = BradPageDTO.req_for_draft_publish_update
_res_for_all_content = BradPageDTO.res_all_content
_res_all_draft_pub = BradPageDTO.res_all_draft_pub
_res_for_preview_page = BradPageDTO.res_for_preview_page
_req_for_image_upload = BradPageDTO.req_for_image_upload
_res_for_image_upload = BradPageDTO.res_for_image_upload
_res_all_system_pages = BradPageDTO.res_all_system_pages


@api.route("api/v1.0/brand/page/<page_id>")
class BrandPageOpe(Resource):
    @api.marshal_with(_res_page_by_id)
    @token_required
    def get(self, page_id):
        return get_page(page_id)

    @token_required
    def delete(self, page_id):
        return delete_page(page_id=page_id)


@api.route("api/v1.0/template/<template_id>/brand/<brand_id>/data")
class IssueTemplate(Resource):
    @api.marshal_with(_res_issue_template_before_save)
    def get(self, template_id, brand_id):
        return issue_template_before_save(template_id, brand_id)


@api.route("api/v1.0/brand/<brand_id>/page")
class BrandPageOperation(Resource):
    @api.expect(_req_for_draft_publish)
    @api.marshal_with(_res_for_draft_publish)
    @token_required
    def post(self, brand_id):
        return save_publish_and_draft(brand_id, data=request.json)


@api.route("api/v1.0/brand/<brand_id>/page/<page_id>")
class BrandPageOperationUpdate(Resource):
    @api.expect(_req_for_draft_publish_update)
    @api.marshal_with(_res_for_draft_publish)
    @token_required
    def put(self, brand_id, page_id):
        return update_page_by_id(brand_id, page_id, data=request.json)


@api.route("api/v1.0/brand/<brand_id>/pages")
class FetchStatusPages(Resource):
    @api.marshal_with(_res_all_draft_pub)
    # @token_required
    def get(self, brand_id):
        status = request.args.get('status')
        category = request.args.get('category')
        args = request.args
        search = args.get('search', '')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return get_all_draft_or_published_pages(brand_id, status, search, category, page, limit)


@api.route("api/v1.0/pages")
class SystemBrandPages(Resource):
    @api.marshal_with(_res_all_system_pages)
    def get(self):
        args = request.args
        category = request.args.get('category')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return get_all_system_pages(category, page, limit)


@api.route("api/v1.0/brand/page/<page_id>/preview")
class BrandPageOperation(Resource):
    @api.marshal_with(_res_for_preview_page)
    @token_required
    def get(self, page_id):
        return preview_page(page_id)


@api.route("api/v1.0/imageupload/brand/<brand_id>")
class BrandPageImage(Resource):
    @api.expect(_req_for_image_upload)
    @api.marshal_with(_res_for_image_upload)
    @token_required
    def post(self, brand_id):
        return upload_images_api(brand_id, data=request.json)


@api.route("api/v1.0/brand/<name>/brandpage")
class BrandPublishedPage(Resource):
    @api.marshal_with(_res_for_all_content)
    def get(self, name):
        args = request.args
        category = request.args.get('category')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        # searchKey = args.get('searchKey')
        return get_all_contents(name, page, limit, category)


@api.route("api/v1.0/brand/<brand_id>/page/<page_id>/duplicate")
class BrandDuplicatePage(Resource):
    @api.marshal_with(_res_for_draft_publish)
    def get(self, brand_id, page_id):
        return duplicate_page(brand_id=brand_id, page_id=page_id)
