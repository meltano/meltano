from flask import jsonify, request

from .embeds_helper import EmbedsHelper, InvalidEmbedToken
from meltano.api.api_blueprint import APIBlueprint
from meltano.api.models import db
from meltano.api.security import block_if_api_auth_required


embedsBP = APIBlueprint("embeds", __name__, require_authentication=False)


@embedsBP.errorhandler(InvalidEmbedToken)
def _handle(ex):
    return (
        jsonify(
            {
                "error": True,
                "code": f"No matching resource found or this resource is no longer public.",
            }
        ),
        400,
    )


@embedsBP.route("/embed/<token>", methods=["GET"])
def get_embed(token):
    today = request.args.get("today", None)

    embeds_helper = EmbedsHelper()
    response_data = embeds_helper.get_embed_from_token(db.session, token, today=today)

    return jsonify(response_data)


@embedsBP.route("/embed", methods=["POST"])
@block_if_api_auth_required
def embed():
    post_data = request.get_json()
    resource_id = post_data["resource_id"]
    resource_type = post_data["resource_type"]
    today = post_data.get("today", None)
    embeds_helper = EmbedsHelper()
    response_data = embeds_helper.generate_embed_snippet(
        db.session, resource_id, resource_type, today=today
    )

    return jsonify(response_data)
