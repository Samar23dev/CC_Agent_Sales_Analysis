"""
GroMo AI Sales Coach - API Test

This script tests all endpoints of the GroMo AI Sales Coach API using the sample data
and saves the results to a file named 'output.json'.
"""

import requests
import json
import random
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
base_url = "http://localhost:5000"
api_key = "test-api-key"

# Headers for API requests
headers = {
    "Content-Type": "application/json",
    "X-API-Key": api_key
}

def load_sample_data():
    """Load sample data from JSON files."""
    
    data = {}
    
    # Load agents
    try:
        with open('data/agents.json', 'r') as f:
            data['agents'] = json.load(f)
    except Exception as e:
        print(f"Error loading agents data: {str(e)}")
        data['agents'] = []
    
    # Load cards
    try:
        with open('data/credit_cards.json', 'r') as f:
            data['cards'] = json.load(f)
    except Exception as e:
        print(f"Error loading cards data: {str(e)}")
        data['cards'] = []
    
    # Load sales
    try:
        with open('data/sales.json', 'r') as f:
            data['sales'] = json.load(f)
    except Exception as e:
        print(f"Error loading sales data: {str(e)}")
        data['sales'] = []
    
    return data

def test_api_health():
    """Test the API health endpoint."""
    
    print("\n=== Testing API Health ===")
    try:
        response = requests.get(f"{base_url}/")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("API is running")
            return {
                "endpoint": "/",
                "status_code": response.status_code,
                "response": response.json(),
                "success": True
            }
        else:
            print(f"API health check failed with status code: {response.status_code}")
            return {
                "endpoint": "/",
                "status_code": response.status_code,
                "response": None,
                "success": False
            }
    except Exception as e:
        print(f"Error testing API health: {str(e)}")
        return {
            "endpoint": "/",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        }

def test_agent_endpoints(sample_data):
    """Test the agent-related endpoints."""
    
    results = []
    
    if not sample_data['agents']:
        print("No agent data available for testing")
        return results
    
    print("\n=== Testing Agent Endpoints ===")
    
    # Select a random agent
    agent = random.choice(sample_data['agents'])
    agent_id = agent['agent_id']
    
    print(f"Testing with agent: {agent['name']} (ID: {agent_id})")
    
    # Test agent performance
    print("\nTesting Agent Performance...")
    try:
        response = requests.get(f"{base_url}/api/agent/performance/{agent_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/agent/performance/{agent_id}",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing agent performance: {str(e)}")
        results.append({
            "endpoint": f"/api/agent/performance/{agent_id}",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Test agent dashboard
    print("\nTesting Agent Dashboard...")
    try:
        response = requests.get(f"{base_url}/api/agent/dashboard/{agent_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/agent/dashboard/{agent_id}",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing agent dashboard: {str(e)}")
        results.append({
            "endpoint": f"/api/agent/dashboard/{agent_id}",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Test agent insights
    print("\nTesting Agent Insights...")
    try:
        response = requests.get(f"{base_url}/api/agent/insights/{agent_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/agent/insights/{agent_id}",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing agent insights: {str(e)}")
        results.append({
            "endpoint": f"/api/agent/insights/{agent_id}",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    return results

def test_card_endpoints(sample_data):
    """Test the card-related endpoints."""
    
    results = []
    
    if not sample_data['cards'] or not sample_data['agents']:
        print("No card or agent data available for testing")
        return results
    
    print("\n=== Testing Card Endpoints ===")
    
    # Test card performance
    print("\nTesting Card Performance...")
    try:
        response = requests.get(f"{base_url}/api/card/performance", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": "/api/card/performance",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing card performance: {str(e)}")
        results.append({
            "endpoint": "/api/card/performance",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Select a random agent
    agent = random.choice(sample_data['agents'])
    agent_id = agent['agent_id']
    
    # Test card recommendations
    print("\nTesting Card Recommendations...")
    try:
        response = requests.get(f"{base_url}/api/card/recommend/{agent_id}?limit=5", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/card/recommend/{agent_id}?limit=5",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing card recommendations: {str(e)}")
        results.append({
            "endpoint": f"/api/card/recommend/{agent_id}?limit=5",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Test card comparison
    print("\nTesting Card Comparison...")
    if len(sample_data['cards']) >= 3:
        card_ids = [card['card_id'] for card in random.sample(sample_data['cards'], 3)]
        
        try:
            response = requests.post(
                f"{base_url}/api/card/compare",
                headers=headers,
                json={"card_ids": card_ids}
            )
            
            print(f"Status Code: {response.status_code}")
            
            results.append({
                "endpoint": "/api/card/compare",
                "request_body": {"card_ids": card_ids},
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else None,
                "success": response.status_code == 200
            })
        except Exception as e:
            print(f"Error testing card comparison: {str(e)}")
            results.append({
                "endpoint": "/api/card/compare",
                "request_body": {"card_ids": card_ids},
                "status_code": None,
                "response": None,
                "error": str(e),
                "success": False
            })
    
    return results

def test_script_endpoints(sample_data):
    """Test the script-related endpoints."""
    
    results = []
    
    if not sample_data['cards'] or not sample_data['agents']:
        print("No card or agent data available for testing")
        return results
    
    print("\n=== Testing Script Endpoints ===")
    
    # Select a random card and agent
    card = random.choice(sample_data['cards'])
    card_id = card['card_id']
    
    agent = random.choice(sample_data['agents'])
    agent_id = agent['agent_id']
    
    # Test script generation
    print("\nTesting Script Generation...")
    try:
        response = requests.get(f"{base_url}/api/script/generate/{card_id}?agent_id={agent_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/script/generate/{card_id}?agent_id={agent_id}",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing script generation: {str(e)}")
        results.append({
            "endpoint": f"/api/script/generate/{card_id}?agent_id={agent_id}",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Test objection handling
    print("\nTesting Objection Handling...")
    try:
        response = requests.get(f"{base_url}/api/script/objections/{card_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/script/objections/{card_id}",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing objection handling: {str(e)}")
        results.append({
            "endpoint": f"/api/script/objections/{card_id}",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    return results

def test_lead_endpoints(sample_data):
    """Test the lead-related endpoints."""
    
    results = []
    
    if not sample_data['agents'] or not sample_data['cards']:
        print("No agent or card data available for testing")
        return results
    
    print("\n=== Testing Lead Endpoints ===")
    
    # Select a random agent
    agent = random.choice(sample_data['agents'])
    agent_id = agent['agent_id']
    
    # Test lead recommendations
    print("\nTesting Lead Recommendations...")
    try:
        response = requests.get(f"{base_url}/api/lead/recommend/{agent_id}?limit=5", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/lead/recommend/{agent_id}?limit=5",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing lead recommendations: {str(e)}")
        results.append({
            "endpoint": f"/api/lead/recommend/{agent_id}?limit=5",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Test success prediction
    print("\nTesting Success Prediction...")
    card = random.choice(sample_data['cards'])
    card_id = card['card_id']
    
    # Generate sample customer data
    customer_data = {
        "age": random.randint(25, 60),
        "income": random.randint(300000, 1500000),
        "employment_type": random.choice(["Salaried", "Self-Employed", "Business"]),
        "credit_score": random.randint(650, 850)
    }
    
    prediction_data = {
        "customer_data": customer_data,
        "card_id": card_id,
        "agent_id": agent_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/lead/predict-success",
            headers=headers,
            json=prediction_data
        )
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": "/api/lead/predict-success",
            "request_body": prediction_data,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing success prediction: {str(e)}")
        results.append({
            "endpoint": "/api/lead/predict-success",
            "request_body": prediction_data,
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    return results

def test_forecast_endpoints(sample_data):
    """Test the forecast-related endpoints."""
    
    results = []
    
    if not sample_data['agents']:
        print("No agent data available for testing")
        return results
    
    print("\n=== Testing Forecast Endpoints ===")
    
    # Select a random agent
    agent = random.choice(sample_data['agents'])
    agent_id = agent['agent_id']
    
    # Test commission forecast
    print("\nTesting Commission Forecast...")
    try:
        response = requests.get(f"{base_url}/api/forecast/{agent_id}?months=6", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/forecast/{agent_id}?months=6",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing commission forecast: {str(e)}")
        results.append({
            "endpoint": f"/api/forecast/{agent_id}?months=6",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    # Test optimization suggestions
    print("\nTesting Optimization Suggestions...")
    try:
        response = requests.get(f"{base_url}/api/forecast/optimization/{agent_id}", headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        results.append({
            "endpoint": f"/api/forecast/optimization/{agent_id}",
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "success": response.status_code == 200
        })
    except Exception as e:
        print(f"Error testing optimization suggestions: {str(e)}")
        results.append({
            "endpoint": f"/api/forecast/optimization/{agent_id}",
            "status_code": None,
            "response": None,
            "error": str(e),
            "success": False
        })
    
    return results

def run_all_tests():
    """Run all API tests and save results to output.json."""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"Starting API tests at {timestamp}...")
    print("Loading sample data...")
    sample_data = load_sample_data()
    
    if not sample_data['agents'] or not sample_data['cards'] or not sample_data['sales']:
        print("Error: Sample data not available. Please run the sample data generator first.")
        return
    
    # Check if API is running
    api_health = test_api_health()
    if not api_health["success"]:
        print("API is not running. Please start the Flask application first.")
        return
    
    # Initialize results dictionary
    test_results = {
        "timestamp": timestamp,
        "api_health": api_health,
        "agent_endpoints": [],
        "card_endpoints": [],
        "script_endpoints": [],
        "lead_endpoints": [],
        "forecast_endpoints": [],
        "summary": {
            "total_endpoints": 0,
            "successful": 0,
            "failed": 0
        }
    }
    
    # Run all tests
    print("\nRunning all endpoint tests...")
    
    # Agent endpoints
    agent_results = test_agent_endpoints(sample_data)
    test_results["agent_endpoints"] = agent_results
    
    # Card endpoints
    card_results = test_card_endpoints(sample_data)
    test_results["card_endpoints"] = card_results
    
    # Script endpoints
    script_results = test_script_endpoints(sample_data)
    test_results["script_endpoints"] = script_results
    
    # Lead endpoints
    lead_results = test_lead_endpoints(sample_data)
    test_results["lead_endpoints"] = lead_results
    
    # Forecast endpoints
    forecast_results = test_forecast_endpoints(sample_data)
    test_results["forecast_endpoints"] = forecast_results
    
    # Calculate summary
    all_results = (
        agent_results + 
        card_results + 
        script_results + 
        lead_results + 
        forecast_results
    )
    
    test_results["summary"]["total_endpoints"] = len(all_results) + 1  # +1 for API health
    test_results["summary"]["successful"] = sum(1 for r in all_results if r["success"]) + (1 if api_health["success"] else 0)
    test_results["summary"]["failed"] = test_results["summary"]["total_endpoints"] - test_results["summary"]["successful"]
    
    # Save results to output.json
    with open('output.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print("\nAll tests completed.")
    print(f"Total endpoints tested: {test_results['summary']['total_endpoints']}")
    print(f"Successful: {test_results['summary']['successful']}")
    print(f"Failed: {test_results['summary']['failed']}")
    print("Test results saved to 'output.json'")

# Run the tests
if __name__ == "__main__":
    run_all_tests()
