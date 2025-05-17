# Credit Card Sales Data Generator and Analysis

![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

A comprehensive system for generating and analyzing synthetic credit card sales data using MongoDB. This project simulates a real-world credit card sales environment with agents, different card types, and sales performance analytics.

## 🌟 Features

- Generate synthetic credit card data with realistic attributes
- Simulate sales agents across multiple cities
- Create realistic sales transactions
- Perform advanced analytics on sales performance
- Export data to JSON for further analysis
- Calculate card performance metrics by city

## 📊 Sample Data Overview

### Credit Card Example
```json
{
    "card_id": "CC100000",
    "name": "Premium Select Card",
    "benefits": [
        "Concierge Service",
        "Airport Meet & Greet",
        "Golf Program"
    ],
    "eligibility": "Income > 1500000 per annum",
    "joining_fee": 4999,
    "annual_fee": 2999,
    "interest_rate": 26.74,
    "credit_limit_range": "₹90000 - ₹640000",
    "reward_rate": "3% on shopping"
}
```

### Analysis Output Example
```
===== TOP PERFORMING CREDIT CARD IN CHENNAI =====

Card: Rewards Plus Card (CC100013)
Performance Metrics:
- Approval Rate: 100.00%
- Average Commission: ₹3465.50
- Total Applications: 2
- Successful Sales: 2

Features:
- Benefits: Lounge Access, Reward Points, Cashback
- Eligibility: Income > 1100000 per annum
- Interest Rate: 34.54%
- Reward Rate: 1% on travel
```

## 🚀 Prerequisites

1. **Python 3.7+**
2. **MongoDB Community Server**
   - [Download MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Install and ensure it's running on port 27017 (default)

## 💻 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Samar23dev/CC_Agent_Sales_Analysis
   cd CC_Agent_Sales_Analysis
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MongoDB**
   - Create `.env` file:
     ```
     MONGODB_URI=mongodb://localhost:27017/
     DB_NAME=credit_card_sales
     ```

## 🏃‍♂️ Running the Application

1. **Start MongoDB**
   ```bash
   # Windows
   net start MongoDB

   # Linux
   sudo systemctl start mongod

   # Mac
   brew services start mongodb-community
   ```

2. **Run the script**
   ```bash
   python datacollection2.py
   ```

## 📁 Project Structure

```
CC_Agent_Sales_Analysis/
├── datacollection2.py     # Main script
├── requirements.txt       # Dependencies
├── README.md             # Documentation
├── .env                  # Configuration
└── data/                 # Generated data
    ├── credit_cards.json
    ├── agents.json
    ├── sales.json
    └── output.txt
```

## 📊 Generated Data Types

1. **Credit Cards** (15 records)
   - Multiple card types (Platinum, Gold, etc.)
   - Various benefits and reward rates
   - Different eligibility criteria

2. **Agents** (30 records)
   - Distributed across major cities
   - Performance metrics
   - Specializations

3. **Sales Data** (500 records)
   - Transaction details
   - Customer information
   - Application processing

## 🔍 Analysis Features

- Card performance by city
- Approval rate analysis
- Commission calculations
- Time-weighted performance metrics
- Demographic fit scoring
- Consistency scoring

## 🛠 Troubleshooting

1. **MongoDB Connection Issues**
   ```bash
   # Check MongoDB status
   mongosh
   # Should connect to mongodb://localhost:27017
   ```

2. **Data Generation Issues**
   - Ensure write permissions in data/ directory
   - Check MongoDB disk space
   - Verify MongoDB service status

## 📈 Statistics

Current dataset size:
- Credit Cards: 15 records
- Agents: 30 records
- Sales Records: 500 records

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Samar Mittal**
- GitHub: [@Samar23dev](https://github.com/Samar23dev)

---
⭐️ Star this repo if you find it helpful! 