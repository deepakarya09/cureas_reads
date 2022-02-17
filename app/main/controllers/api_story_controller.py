from flask_restplus import Resource
from flask import current_app as cur_app
from flask import request
from app.main.services.story.brand_story_services import duplicate_story, get_all_draft_or_published_story, get_story, issue_story_template_before_save, post_story_publish_and_draft, remove_story_from_search, update_story_by_id, get_all_system_story

from app.main.utils.api_story_dto import BrandStoryDTO

api = BrandStoryDTO.api
_res_issue_template_before_save = BrandStoryDTO.res_issue_template_before_save
_post_req_for_draft_publish = BrandStoryDTO.post_req_for_draft_publish
_res_for_draft_publish = BrandStoryDTO.res_for_draft_publish
_req_for_draft_publish_update = BrandStoryDTO.post_req_for_draft_publish_update
_res_story_by_id = BrandStoryDTO.res_story_by_id
_res_get_all_draft_and_publish_story = BrandStoryDTO.res_get_all_draft_and_publish_story

_res_get_all_system = BrandStoryDTO.res_all_Storye_pages


@api.route("api/v1.0/brand/story/<story_id>")
class BrandStoryOpe(Resource):
    @api.marshal_with(_res_story_by_id)
    def get(self, story_id):
        return get_story(story_id)

    def delete(self, story_id):
        return remove_story_from_search(story_id=story_id)


@api.route("api/v1.0/story/template/<template_id>/data")
class IssueStoryTemplate(Resource):
    @api.marshal_with(_res_issue_template_before_save)
    def get(self, template_id):
        return issue_story_template_before_save(template_id)


@api.route("api/v1.0/brand/<brand_id>/story")
class BrandStoryOperation(Resource):
    @api.expect(_post_req_for_draft_publish)
    @api.marshal_with(_res_for_draft_publish)
    def post(self, brand_id):
        return post_story_publish_and_draft(brand_id, data=request.json)


@api.route("api/v1.0/brand/<brand_id>/story/<story_id>")
class BrandStoryOperationUpdate(Resource):
    @api.expect(_req_for_draft_publish_update)
    @api.marshal_with(_res_for_draft_publish)
    def put(self, brand_id, story_id):
        return update_story_by_id(brand_id, story_id, data=request.json)


@api.route("api/v1.0/brand/<brand_id>/storys")
class FetchStatusStory(Resource):
    @api.marshal_with(_res_get_all_draft_and_publish_story)
    # @token_required
    def get(self, brand_id):
        status = request.args.get('status')
        active = request.args.get('active')
        category = request.args.get('category')
        args = request.args
        search = args.get('search', '')
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        return get_all_draft_or_published_story(brand_id, status, active, search, category, page, limit)


@api.route("api/v1.0/brand/<brand_id>/story/<story_id>/duplicate")
class BrandDuplicateStory(Resource):
    @api.marshal_with(_res_for_draft_publish)
    def get(self, brand_id, story_id):
        return duplicate_story(brand_id=brand_id, story_id=story_id)


@api.route("api/v1.0/story")
class SystemBrandPages(Resource):
    @api.marshal_with(_res_get_all_system)
    def get(self):
        args = request.args
        page = int(args.get('page', cur_app.config['PAGE']))
        limit = int(args.get('limit', cur_app.config['LIMIT']))
        category = request.args.get('category')
        return get_all_system_story(category, page, limit)
