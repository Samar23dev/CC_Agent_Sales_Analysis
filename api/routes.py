"""
GroMo AI Sales Coach - API Routes

This module defines all API routes for the GroMo AI Sales Coach.
It registers these routes with the Flask application.
"""

from flask import Blueprint, jsonify, request

from services.agent_service import AgentService
from services.card_service import CardService
from services.script_service import ScriptService
from services.lead_service import LeadService
from services.forecast_service import ForecastService


# Create blueprints for different API sections
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')
card_bp = Blueprint('card', __name__, url_prefix='/api/card')
script_bp = Blueprint('script', __name__, url_prefix='/api/script')
lead_bp = Blueprint('lead', __name__, url_prefix='/api/lead')
forecast_bp = Blueprint('forecast', __name__, url_prefix='/api/forecast')


# Initialize services
agent_service = AgentService()
card_service = CardService()
script_service = ScriptService()
lead_service = LeadService()
forecast_service = ForecastService()


# Agent Routes
@agent_bp.route('/performance/<agent_id>', methods=['GET'])
def get_agent_performance(agent_id):
    """Get performance metrics for a specific agent."""
    try:
        result = agent_service.analyze_performance(agent_id)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'No data found for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@agent_bp.route('/dashboard/<agent_id>', methods=['GET'])
def get_agent_dashboard(agent_id):
    """Generate a comprehensive dashboard for a specific agent."""
    try:
        result = agent_service.create_dashboard(agent_id)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate dashboard for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@agent_bp.route('/insights/<agent_id>', methods=['GET'])
def get_agent_insights(agent_id):
    """Get personalized insights for a specific agent."""
    try:
        result = agent_service.generate_insights(agent_id)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate insights for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Card Routes
@card_bp.route('/performance', methods=['GET'])
def get_card_performance():
    """Get performance metrics for all cards."""
    try:
        result = card_service.analyze_all_cards()
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@card_bp.route('/recommend/<agent_id>', methods=['GET'])
def recommend_cards(agent_id):
    """Get card recommendations for a specific agent."""
    try:
        # Parse query parameters
        limit = request.args.get('limit', default=5, type=int)
        
        result = card_service.recommend_cards(agent_id, limit=limit)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate recommendations for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@card_bp.route('/compare', methods=['POST'])
def compare_cards():
    """Compare multiple cards."""
    try:
        data = request.get_json()
        if not data or 'card_ids' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing card_ids in request body'
            }), 400
            
        card_ids = data['card_ids']
        result = card_service.compare_cards(card_ids)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Could not compare the specified cards'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Script Routes
@script_bp.route('/generate/<card_id>', methods=['GET'])
def generate_script(card_id):
    """Generate a sales script for a specific card."""
    try:
        # Optional agent_id for personalization
        agent_id = request.args.get('agent_id', default=None)
        
        result = script_service.create_script(card_id, agent_id)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate script for card {card_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@script_bp.route('/objections/<card_id>', methods=['GET'])
def get_objection_handling(card_id):
    """Get objection handling suggestions for a specific card."""
    try:
        result = script_service.get_objection_handling(card_id)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not get objection handling for card {card_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Lead Routes
@lead_bp.route('/recommend/<agent_id>', methods=['GET'])
def recommend_leads(agent_id):
    """Get lead recommendations for a specific agent."""
    try:
        # Parse query parameters
        limit = request.args.get('limit', default=5, type=int)
        
        result = lead_service.recommend_leads(agent_id, limit=limit)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate lead recommendations for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@lead_bp.route('/predict-success', methods=['POST'])
def predict_success():
    """Predict success probability for a potential sale."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400
            
        # Validate required fields
        if 'customer_data' not in data or 'card_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing customer_data or card_id in request body'
            }), 400
            
        result = lead_service.predict_success(
            customer_data=data['customer_data'],
            card_id=data['card_id'],
            agent_id=data.get('agent_id')
        )
        
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Could not predict success probability'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Forecast Routes
@forecast_bp.route('/<agent_id>', methods=['GET'])
def get_forecast(agent_id):
    """Get commission forecast for a specific agent."""
    try:
        # Parse query parameters
        months = request.args.get('months', default=6, type=int)
        
        result = forecast_service.generate_forecast(agent_id, forecast_months=months)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate forecast for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@forecast_bp.route('/optimization/<agent_id>', methods=['GET'])
def get_optimization(agent_id):
    """Get optimization suggestions for a specific agent."""
    try:
        result = forecast_service.get_optimization_suggestions(agent_id)
        if result:
            return jsonify({
                'status': 'success',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Could not generate optimization suggestions for agent {agent_id}'
            }), 404
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def register_routes(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(agent_bp)
    app.register_blueprint(card_bp)
    app.register_blueprint(script_bp)
    app.register_blueprint(lead_bp)
    app.register_blueprint(forecast_bp)
