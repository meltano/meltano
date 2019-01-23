import os
from os.path import join

from flask import Blueprint, jsonify, request
from .reports_helper import ReportsHelper

reportsBP = Blueprint("reports", __name__, url_prefix="/reports")
meltano_model_path = join(os.getcwd(), "model")


@reportsBP.route("/load/<report_name>", methods=["GET"])
def load_report(report_name):
    # file_path = Path(meltano_model_path).joinpath(f"{report_name}.table.m5o")
    # m5o_parse = MeltanoAnalysisFileParser(meltano_model_path)
    # table = m5o_parse.parse_m5o_file(file_path)
    return jsonify({ "success": "it worked!" })


@reportsBP.route("/save", methods=["POST"])
def save_report():
    reports_helper = ReportsHelper()
    post_data = request.get_json()
    response_data = reports_helper.save_report(post_data)
    return jsonify(response_data)
