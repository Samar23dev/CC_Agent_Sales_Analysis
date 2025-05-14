# Credit Card Sales Data Collection System

A Python-based system for collecting and analyzing credit card sales data, including agent performance, card benefits, and sales metrics.

## Features

- Random data generation for credit cards, agents, and sales
- MongoDB integration for data storage
- Performance analysis of credit cards by location
- Detailed sales tracking with customer and application details

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repository-url>
cd credit-card-sales
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up MongoDB:
- Install MongoDB Community Server
- Create a MongoDB Atlas account or use local MongoDB
- Update the connection string in `datacollection.py`

5. Run the script:
```bash
python datacollection.py
```

## Project Structure

- `datacollection.py`: Main script for data generation and analysis
- `requirements.txt`: Python dependencies
- `README.md`: Project documentation

## Data Model

### Credit Cards
- Card ID
- Name
- Benefits
- Eligibility
- Fees
- Interest rates
- Credit limits
- Reward rates

### Agents
- Agent ID
- Name
- Location
- Language
- Experience
- Specialization
- Performance metrics

### Sales
- Agent details
- Card details
- Location
- Customer information
- Application status
- Commission

## Performance Metrics

The system calculates card performance using:
- Approval rate (50%)
- Average commission (30%)
- Sales volume (20%)

## License

MIT License 