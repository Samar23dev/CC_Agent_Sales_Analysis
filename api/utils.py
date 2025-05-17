"""
GroMo AI Sales Coach - API Utilities

This module contains utility functions for the API layer.
"""

import json
from functools import wraps
from flask import request, jsonify


def validate_json(schema=None):
    """
    Decorator to validate JSON request data against a schema.
    
    Args:
        schema: JSON schema to validate against (optional)
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validate request has JSON content
            if not request.is_json:
                return jsonify({
                    'status': 'error',
                    'message': 'Request must contain JSON data'
                }), 400
                
            # Validate schema if provided
            if schema:
                try:
                    # In a real application, you'd use a schema validation library
                    # like jsonschema or marshmallow
                    # For simplicity, we're just checking required fields
                    data = request.get_json()
                    for field in schema:
                        if field not in data:
                            return jsonify({
                                'status': 'error',
                                'message': f'Missing required field: {field}'
                            }), 400
                except Exception as e:
                    return jsonify({
                        'status': 'error',
                        'message': f'Invalid JSON data: {str(e)}'
                    }), 400
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def format_response(data=None, message=None, status='success'):
    """
    Format a consistent API response.
    
    Args:
        data: Response data (optional)
        message: Response message (optional)
        status: Response status (default: 'success')
        
    Returns:
        Formatted response dictionary
    """
    response = {'status': status}
    
    if data is not None:
        response['data'] = data
        
    if message is not None:
        response['message'] = message
        
    return response


def parse_int_param(param, default=None, min_value=None, max_value=None):
    """
    Parse and validate an integer parameter from the request.
    
    Args:
        param: Parameter name
        default: Default value if parameter is not provided
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        
    Returns:
        Parsed and validated integer value
    """
    value = request.args.get(param, default=default, type=int)
    
    if value is None:
        return default
        
    if min_value is not None and value < min_value:
        return min_value
        
    if max_value is not None and value > max_value:
        return max_value
        
    return value


def requires_auth(f):
    """
    Decorator for endpoints that require authentication.
    
    In a real implementation, this would validate an API key or token.
    For this example, it's just a placeholder.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # In a real application, you would validate authentication here
        # For now, we're just checking if the API key header exists
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'Authentication required'
            }), 401
            
        # In a real application, you would validate the API key
        # For this example, we accept any non-empty API key
        
        return f(*args, **kwargs)
    return decorated
