# GroMo AI Sales Coach

## Overview

GroMo AI Sales Coach is an intelligent assistant designed to help GroMo Partners (financial micro-entrepreneurs) maximize their sales performance and increase their commission earnings. It uses data analysis and machine learning to provide personalized recommendations, sales strategies, and performance insights.

## Project Structure

```
gromo_ai_sales_coach/
├── app.py                  # Flask application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
│
├── api/                    # API endpoints
│   ├── __init__.py
│   ├── routes.py           # API route definitions
│   └── utils.py            # API utilities
│
├── models/                 # ML model definitions
│   ├── __init__.py
│   ├── success_predictor.py  # Application success prediction model
│   └── commission_predictor.py  # Commission prediction model
│
├── services/               # Business logic services
│   ├── __init__.py
│   ├── agent_service.py    # Agent performance analysis
│   ├── card_service.py     # Card performance and recommendation
│   ├── script_service.py   # Sales script generation
│   ├── lead_service.py     # Lead recommendation service
│   └── forecast_service.py # Commission forecasting service
│
├── data/                   # Data management
│   ├── __init__.py
│   └── data_loader.py      # Data loading functions
│
└── utils/                  # Utility functions
    ├── __init__.py
    ├── visualization.py    # Data visualization utilities
    └── metrics.py          # Performance metrics calculation
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- MongoDB (optional, for larger deployments)

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/your-team/gromo-ai-sales-coach.git
   cd gromo-ai-sales-coach
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables (optional):
   Create a `.env` file in the project root with:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=gromo_ai_coach
   FLASK_ENV=development
   ```

4. Start the Flask API server:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000/`.

## API Endpoints and Usage

### Agent Performance Analysis

#### Get Agent Performance

```
GET /api/agent/performance/{agent_id}
```

Retrieves detailed performance metrics for a specific agent.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "agent_info": {
      "agent_id": "AG1001",
      "name": "John Doe",
      "location": "Mumbai",
      "experience_years": 3
    },
    "overall": {
      "total_sales": 87,
      "successful_sales": 53,
      "success_rate": 0.609,
      "total_commission": 132500,
      "avg_commission": 2500
    },
    "card_performance": [...],
    "monthly_performance": [...],
    "segment_performance": [...]
  }
}
```

#### Get Agent Dashboard

```
GET /api/agent/dashboard/{agent_id}
```

Generates a comprehensive performance dashboard for an agent, including charts and visualizations.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "performance": {...},
    "charts": {
      "monthly_trend": "base64_encoded_image",
      "card_performance": "base64_encoded_image",
      "segment_performance": "base64_encoded_image"
    },
    "insights": {...}
  }
}
```

#### Get Agent Insights

```
GET /api/agent/insights/{agent_id}
```

Provides personalized insights and recommendations for an agent based on their performance.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "strengths": [
      "Your approval rate of 60.9% is above the network average of 54.3%, indicating strong customer qualification skills."
    ],
    "areas_for_improvement": [
      "You're heavily focused on a single card type. Diversifying your product mix could increase your overall earnings."
    ],
    "recommendations": [
      "Increase focus on Premium Gold Card, which generates ₹3,500 average commission with 65.2% success rate."
    ]
  }
}
```

### Card Recommendations

#### Get Card Performance

```
GET /api/card/performance
```

Retrieves performance metrics for all cards across the network.

#### Get Card Recommendations

```
GET /api/card/recommend/{agent_id}?limit=5
```

Provides personalized card recommendations for a specific agent based on their performance history.

**Example Response:**
```json
{
  "status": "success",
  "data": [
    {
      "card_id": "CC100005",
      "name": "Premium Gold Card",
      "success_rate": 0.652,
      "avg_commission": 3500,
      "total_sales": 27,
      "benefits": ["Lounge Access", "Reward Points", "Travel Insurance"],
      "fit_score": 0.89,
      "explanation": "Premium Gold Card has an approval rate of 65.2% and generates an average commission of ₹3,500 per successful sale. You've had success with this card, achieving a 72.2% approval rate."
    },
    ...
  ]
}
```

#### Compare Cards

```
POST /api/card/compare
```

Compares multiple cards based on their features and performance metrics.

**Request Body:**
```json
{
  "card_ids": ["CC100005", "CC100008", "CC100012"]
}
```

### Sales Scripts

#### Generate Sales Script

```
GET /api/script/generate/{card_id}?agent_id={agent_id}
```

Generates a personalized sales script for a specific card, optionally tailored to an agent's selling style.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "card_name": "Premium Gold Card",
    "introduction": {
      "greeting": "Hello, this is [Your Name] from GroMo. How are you doing today? I'd like to tell you about a fantastic credit card that might be perfect for your needs.",
      "opening": "I'd like to introduce you to Premium Gold Card, one of our most popular options with excellent benefits that match your spending habits.",
      "transition": "May I take a few minutes to explain how this card can benefit you?"
    },
    "qualification": {...},
    "benefits_presentation": {...},
    "objection_handling": {...},
    "closing": {...},
    "application_process": {...}
  }
}
```

#### Get Objection Handling

```
GET /api/script/objections/{card_id}
```

Provides objection handling techniques for a specific card based on common customer concerns.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "card_name": "Premium Gold Card",
    "objections": [
      {
        "objection": "Annual Fee",
        "response": "I understand your concern about fees. The good news is that this card has no joining fee. The benefits you'll receive far outweigh the costs, including Lounge Access and Reward Points.",
        "frequency": 12
      },
      ...
    ]
  }
}
```

### Lead Recommendations

#### Get Lead Recommendations

```
GET /api/lead/recommend/{agent_id}?limit=5
```

Recommends potential leads for an agent based on their performance history and success patterns.

**Example Response:**
```json
{
  "status": "success",
  "data": [
    {
      "customer": {
        "name": "Lead 3842",
        "age": 42,
        "income": 750000,
        "employment_type": "Salaried",
        "credit_score": 780,
        "contact_number": "+91 9876543210",
        "email": "lead3842@example.com"
      },
      "card_id": "CC100005",
      "card_details": {...},
      "success_probability": 0.85,
      "expected_commission": 3500,
      "key_factors": [...]
    },
    ...
  ]
}
```

#### Predict Success Probability

```
POST /api/lead/predict-success
```

Predicts the success probability and expected commission for a potential sale.

**Request Body:**
```json
{
  "customer_data": {
    "age": 42,
    "income": 750000,
    "employment_type": "Salaried",
    "credit_score": 780
  },
  "card_id": "CC100005",
  "agent_id": "AG1001"
}
```

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "success_probability": 0.85,
    "expected_commission": 3500,
    "key_factors": [
      {
        "factor": "Excellent credit score",
        "impact": "positive",
        "description": "Credit score of 780 is excellent (750+)"
      },
      {
        "factor": "Income well above requirement",
        "impact": "positive",
        "description": "Customer income (₹750,000) exceeds the minimum requirement of ₹500,000"
      }
    ]
  }
}
```

### Commission Forecasting

#### Get Commission Forecast

```
GET /api/forecast/{agent_id}?months=6
```

Generates a commission forecast for a specific agent based on their historical performance.

**Example Response:**
```json
{
  "status": "success",
  "data": {
    "agent_info": {...},
    "historical": [...],
    "forecast": [
      {
        "month": "June 2025",
        "total_sales": 15,
        "successful_sales": 9,
        "success_rate": 0.6,
        "commission": 22500,
        "cumulative_commission": 22500
      },
      ...
    ],
    "summary": {
      "forecast_months": 6,
      "total_forecast_sales": 96,
      "total_forecast_commission": 144000,
      "avg_monthly_commission": 24000,
      "projected_growth": 0.05
    },
    "optimization": [...]
  }
}
```

#### Get Optimization Suggestions

```
GET /api/forecast/optimization/{agent_id}
```

Provides optimization suggestions to help an agent increase their earnings.

**Example Response:**
```json
{
  "status": "success",
  "data": [
    {
      "category": "Improve Approval Rate",
      "description": "Your current approval rate of 60.9% can be improved. Better pre-screening of customers can increase this to 70-80%.",
      "impact": "Increasing your approval rate to 70% could boost your monthly commission by approximately 20%.",
      "action_items": [
        "Pre-check customer credit scores before application",
        "Verify income documents thoroughly",
        "Match customers with cards they're most likely to qualify for",
        "Use the AI Success Predictor tool before submitting applications"
      ]
    },
    ...
  ]
}
```

## How It Works

### Data Flow

1. The client (GroMo mobile app) sends requests to the Flask API endpoints
2. The API routes direct requests to the appropriate service methods
3. Services process the requests and retrieve data through the DataLoader
4. Services apply business logic and call models for predictions when needed
5. Results are formatted and returned to the client

### Machine Learning Models

1. **Success Predictor**: Predicts the probability of a credit card application being approved based on customer attributes and card characteristics. Uses a Random Forest classifier.

2. **Commission Predictor**: Predicts the expected commission amount for a successful sale based on customer attributes and card characteristics. Uses a Gradient Boosting regressor.

### Key Components

1. **Agent Service**: Analyzes agent performance, identifies strengths and weaknesses, and generates personalized insights.

2. **Card Service**: Recommends cards based on agent's individual performance history and success patterns, without location-based predictions.

3. **Script Service**: Generates personalized sales scripts and objection handling techniques based on observed successes and failures.

4. **Lead Service**: Recommends potential leads with high success probability based on agent's historical performance.

5. **Forecast Service**: Projects future earnings based on historical data and provides suggestions for optimization.

### Integration with GroMo App

The system is designed to be easily integrated with the existing GroMo mobile app:

1. **API Integration**: All functionality is exposed through RESTful API endpoints that can be called from the mobile app.

2. **Visualization Support**: Charts and visualizations are returned as base64-encoded images that can be displayed in the app.

3. **Real-time Assistance**: Success prediction endpoints can be used during customer interactions to guide agents.

4. **Personalized Dashboards**: Agent-specific dashboards can be integrated into the app's interface.

## Usage Examples

### Example 1: Analyzing Agent Performance

```python
import requests

# Get agent performance
response = requests.get('http://localhost:5000/api/agent/performance/AG1001')
performance = response.json()['data']

print(f"Success Rate: {performance['overall']['success_rate']:.1%}")
print(f"Total Commission: ₹{performance['overall']['total_commission']:,}")

# Get top performing cards for this agent
for card in performance['card_performance'][:3]:
    print(f"Card: {card['name']}, Commission: ₹{card['commission']:,}")
```

### Example 2: Getting Lead Recommendations

```python
import requests

# Get lead recommendations
response = requests.get('http://localhost:5000/api/lead/recommend/AG1001?limit=3')
leads = response.json()['data']

for lead in leads:
    print(f"Lead: {lead['customer']['name']}")
    print(f"Card: {lead['card_details']['name']}")
    print(f"Success Probability: {lead['success_probability']:.1%}")
    print(f"Expected Commission: ₹{lead['expected_commission']:,}")
    print("---")
```

### Example 3: Predicting Sale Success

```python
import requests

# Customer data
customer = {
    "age": 42,
    "income": 750000,
    "employment_type": "Salaried",
    "credit_score": 780
}

# Predict success
response = requests.post(
    'http://localhost:5000/api/lead/predict-success',
    json={
        "customer_data": customer,
        "card_id": "CC100005",
        "agent_id": "AG1001"
    }
)

prediction = response.json()['data']
print(f"Success Probability: {prediction['success_probability']:.1%}")
print(f"Expected Commission: ₹{prediction['expected_commission']:,}")

# Print key factors
for factor in prediction['key_factors']:
    impact = "✅" if factor['impact'] == 'positive' else "❌"
    print(f"{impact} {factor['factor']}: {factor['description']}")
```

## Future Enhancements

1. **Real-time Call Assistance**: Live suggestions during customer calls
2. **Voice Analysis**: Sentiment and speech pattern analysis for better coaching
3. **Mobile Integration**: Deeper integration with the GroMo app
4. **Expanded Product Coverage**: Support for more financial products
5. **Community Learning**: Sharing strategies among partners

## Made with passion By

- [SATWIK RAI] - [SOLE OWNER AND DEVELOPER]

