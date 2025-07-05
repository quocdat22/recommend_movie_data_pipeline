from airflow.plugins_manager import AirflowPlugin
from flask import Blueprint, Response

health_check_bp = Blueprint('health_check', __name__, url_prefix='/health')

@health_check_bp.route('/')
def health():
    return Response('OK', status=200)

class HealthCheckPlugin(AirflowPlugin):
    name = 'health_check'
    flask_blueprints = [health_check_bp]