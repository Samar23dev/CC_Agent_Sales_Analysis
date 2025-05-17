# Credit Card Sales Data Generator

This project generates and analyzes synthetic credit card sales data using MongoDB for storage and analysis.

## Prerequisites

1. **Python 3.7+**
2. **MongoDB Community Server**
   - [Download MongoDB Community Server](https://www.mongodb.com/try/download/community)
   - Install MongoDB on your system
   - Make sure the MongoDB service is running on port 27017 (default port)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Samar23dev/CC_Agent_Sales_Analysis
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a .env file (optional - for custom configuration)**
   ```
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=credit_card_sales
   ```

5. **Verify MongoDB is running**
   ```bash
   # Windows
   net start MongoDB

   # Linux
   sudo systemctl status mongod

   # Mac
   brew services list
   ```

## Running the Application

1. **Start MongoDB** (if not already running)
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

## Project Structure

- `datacollection2.py`: Main script for data generation and analysis
- `data/`: Directory containing exported JSON files
  - `credit_cards.json`: Generated credit card data
  - `agents.json`: Generated agent data
  - `sales.json`: Generated sales data

## Generated Data

The script generates three types of data:

1. **Credit Cards**
   - Various card types (Platinum, Gold, etc.)
   - Benefits, fees, and reward rates
   - Eligibility criteria

2. **Agents**
   - Agent details and locations
   - Performance metrics
   - Contact information

3. **Sales Data**
   - Transaction records
   - Customer information
   - Application details

## Troubleshooting

1. **MongoDB Connection Issues**
   - Verify MongoDB is running: Check the service status
   - Default port (27017) is available and not blocked
   - MongoDB service has necessary permissions

2. **Data Generation Issues**
   - Check disk space for JSON exports
   - Verify write permissions in the data directory

## Error Codes

- Exit code 1: MongoDB connection failure
- Exit code 1: Data validation failure

## Dependencies

- pymongo
- faker
- python-dotenv
- numpy

## License

[Your License Here]

## Contributing

[Your Contributing Guidelines Here] 