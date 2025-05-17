"""
GroMo AI Sales Coach - Data Loader

This module provides functionality for loading and preprocessing data
for the GroMo AI Sales Coach application.
"""

import os
import json
import pandas as pd
from datetime import datetime
import pymongo
from pymongo import MongoClient

from config import Config


class DataLoader:
    """Data loader for the GroMo AI Sales Coach application."""
    
    def __init__(self):
        """Initialize the Data Loader."""
        self.data_dir = 'data'  # Default data directory
        self.db_uri = Config.MONGODB_URI
        self.db_name = Config.DB_NAME
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Sales data cache
        self._sales_data = None
        self._cards_data = None
        self._agents_data = None
        
        # MongoDB client
        self._mongo_client = None
        self._db_connection = False
    
    def load_sales_data(self):
        """
        Load sales data from JSON file or MongoDB.
        
        Returns:
            DataFrame with sales data
        """
        # Return cached data if available
        if self._sales_data is not None:
            return self._sales_data
            
        # Try loading from MongoDB
        if self._connect_to_mongodb():
            try:
                db = self._mongo_client[self.db_name]
                sales_collection = db['sales']
                
                # Get all documents from the collection
                sales_data = list(sales_collection.find({}))
                
                if sales_data:
                    # Convert MongoDB documents to DataFrame
                    df = pd.DataFrame(sales_data)
                    
                    # Remove MongoDB _id column
                    if '_id' in df.columns:
                        df = df.drop(columns=['_id'])
                    
                    # Process the data
                    df = self._preprocess_sales_data(df)
                    
                    # Cache the data
                    self._sales_data = df
                    
                    return df
            except Exception as e:
                print(f"Error loading data from MongoDB: {str(e)}")
        
        # Fall back to loading from JSON file
        sales_path = os.path.join(self.data_dir, 'sales.json')
        
        if os.path.exists(sales_path):
            try:
                with open(sales_path, 'r') as f:
                    sales_data = json.load(f)
                    
                # Convert to DataFrame
                df = pd.DataFrame(sales_data)
                
                # Process the data
                df = self._preprocess_sales_data(df)
                
                # Cache the data
                self._sales_data = df
                
                return df
            except Exception as e:
                print(f"Error loading sales data from file: {str(e)}")
                return None
        else:
            return None
    
    def load_cards_data(self):
        """
        Load credit card data from JSON file or MongoDB.
        
        Returns:
            DataFrame with credit card data
        """
        # Return cached data if available
        if self._cards_data is not None:
            return self._cards_data
            
        # Try loading from MongoDB
        if self._connect_to_mongodb():
            try:
                db = self._mongo_client[self.db_name]
                cards_collection = db['credit_cards']
                
                # Get all documents from the collection
                cards_data = list(cards_collection.find({}))
                
                if cards_data:
                    # Convert MongoDB documents to DataFrame
                    df = pd.DataFrame(cards_data)
                    
                    # Remove MongoDB _id column
                    if '_id' in df.columns:
                        df = df.drop(columns=['_id'])
                    
                    # Cache the data
                    self._cards_data = df
                    
                    return df
            except Exception as e:
                print(f"Error loading data from MongoDB: {str(e)}")
        
        # Fall back to loading from JSON file
        cards_path = os.path.join(self.data_dir, 'credit_cards.json')
        
        if os.path.exists(cards_path):
            try:
                with open(cards_path, 'r') as f:
                    cards_data = json.load(f)
                    
                # Convert to DataFrame
                df = pd.DataFrame(cards_data)
                
                # Cache the data
                self._cards_data = df
                
                return df
            except Exception as e:
                print(f"Error loading cards data from file: {str(e)}")
                return None
        else:
            return None
    
    def load_agents_data(self):
        """
        Load agent data from JSON file or MongoDB.
        
        Returns:
            DataFrame with agent data
        """
        # Return cached data if available
        if self._agents_data is not None:
            return self._agents_data
            
        # Try loading from MongoDB
        if self._connect_to_mongodb():
            try:
                db = self._mongo_client[self.db_name]
                agents_collection = db['agents']
                
                # Get all documents from the collection
                agents_data = list(agents_collection.find({}))
                
                if agents_data:
                    # Convert MongoDB documents to DataFrame
                    df = pd.DataFrame(agents_data)
                    
                    # Remove MongoDB _id column
                    if '_id' in df.columns:
                        df = df.drop(columns=['_id'])
                    
                    # Process the data
                    df = self._preprocess_agents_data(df)
                    
                    # Cache the data
                    self._agents_data = df
                    
                    return df
            except Exception as e:
                print(f"Error loading data from MongoDB: {str(e)}")
        
        # Fall back to loading from JSON file
        agents_path = os.path.join(self.data_dir, 'agents.json')
        
        if os.path.exists(agents_path):
            try:
                with open(agents_path, 'r') as f:
                    agents_data = json.load(f)
                    
                # Convert to DataFrame
                df = pd.DataFrame(agents_data)
                
                # Process the data
                df = self._preprocess_agents_data(df)
                
                # Cache the data
                self._agents_data = df
                
                return df
            except Exception as e:
                print(f"Error loading agents data from file: {str(e)}")
                return None
        else:
            return None
    
    def save_sales_data(self, data):
        """
        Save sales data to JSON file and MongoDB if available.
        
        Args:
            data: DataFrame or list of dictionaries with sales data
        """
        # Convert DataFrame to list of dictionaries if needed
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        else:
            data_list = data
            
        # Save to JSON file
        sales_path = os.path.join(self.data_dir, 'sales.json')
        
        try:
            with open(sales_path, 'w') as f:
                json.dump(data_list, f, indent=2, default=self._json_serial)
                
            # Update cache
            if isinstance(data, pd.DataFrame):
                self._sales_data = data
            else:
                self._sales_data = pd.DataFrame(data_list)
                self._sales_data = self._preprocess_sales_data(self._sales_data)
                
            # Try saving to MongoDB
            if self._connect_to_mongodb():
                try:
                    db = self._mongo_client[self.db_name]
                    sales_collection = db['sales']
                    
                    # Clear existing data
                    sales_collection.delete_many({})
                    
                    # Insert new data
                    sales_collection.insert_many(data_list)
                except Exception as e:
                    print(f"Error saving data to MongoDB: {str(e)}")
        except Exception as e:
            print(f"Error saving sales data to file: {str(e)}")
    
    def save_cards_data(self, data):
        """
        Save credit card data to JSON file and MongoDB if available.
        
        Args:
            data: DataFrame or list of dictionaries with credit card data
        """
        # Convert DataFrame to list of dictionaries if needed
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        else:
            data_list = data
            
        # Save to JSON file
        cards_path = os.path.join(self.data_dir, 'credit_cards.json')
        
        try:
            with open(cards_path, 'w') as f:
                json.dump(data_list, f, indent=2, default=self._json_serial)
                
            # Update cache
            if isinstance(data, pd.DataFrame):
                self._cards_data = data
            else:
                self._cards_data = pd.DataFrame(data_list)
                
            # Try saving to MongoDB
            if self._connect_to_mongodb():
                try:
                    db = self._mongo_client[self.db_name]
                    cards_collection = db['credit_cards']
                    
                    # Clear existing data
                    cards_collection.delete_many({})
                    
                    # Insert new data
                    cards_collection.insert_many(data_list)
                except Exception as e:
                    print(f"Error saving data to MongoDB: {str(e)}")
        except Exception as e:
            print(f"Error saving cards data to file: {str(e)}")
    
    def save_agents_data(self, data):
        """
        Save agent data to JSON file and MongoDB if available.
        
        Args:
            data: DataFrame or list of dictionaries with agent data
        """
        # Convert DataFrame to list of dictionaries if needed
        if isinstance(data, pd.DataFrame):
            data_list = data.to_dict('records')
        else:
            data_list = data
            
        # Save to JSON file
        agents_path = os.path.join(self.data_dir, 'agents.json')
        
        try:
            with open(agents_path, 'w') as f:
                json.dump(data_list, f, indent=2, default=self._json_serial)
                
            # Update cache
            if isinstance(data, pd.DataFrame):
                self._agents_data = data
            else:
                self._agents_data = pd.DataFrame(data_list)
                self._agents_data = self._preprocess_agents_data(self._agents_data)
                
            # Try saving to MongoDB
            if self._connect_to_mongodb():
                try:
                    db = self._mongo_client[self.db_name]
                    agents_collection = db['agents']
                    
                    # Clear existing data
                    agents_collection.delete_many({})
                    
                    # Insert new data
                    agents_collection.insert_many(data_list)
                except Exception as e:
                    print(f"Error saving data to MongoDB: {str(e)}")
        except Exception as e:
            print(f"Error saving agents data to file: {str(e)}")
    
    def _preprocess_sales_data(self, df):
        """
        Preprocess sales data.
        
        Args:
            df: DataFrame with sales data
            
        Returns:
            Preprocessed DataFrame
        """
        if df is None or len(df) == 0:
            return df
            
        # Convert date strings to datetime
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'])
            except Exception:
                pass
                
        # Extract customer details
        if 'customer_details' in df.columns:
            try:
                # Extract customer age
                df['customer_age'] = df['customer_details'].apply(
                    lambda x: x.get('age', None) if isinstance(x, dict) else None
                )
                
                # Extract customer income
                df['customer_income'] = df['customer_details'].apply(
                    lambda x: x.get('income', None) if isinstance(x, dict) else None
                )
                
                # Extract customer employment type
                df['customer_employment'] = df['customer_details'].apply(
                    lambda x: x.get('employment_type', None) if isinstance(x, dict) else None
                )
                
                # Extract customer credit score
                df['customer_credit_score'] = df['customer_details'].apply(
                    lambda x: x.get('credit_score', None) if isinstance(x, dict) else None
                )
            except Exception:
                pass
                
        # Extract location information
        if 'location' in df.columns:
            try:
                # Extract city
                df['city'] = df['location'].apply(
                    lambda x: x.get('city', None) if isinstance(x, dict) else None
                )
                
                # Extract pincode
                df['pincode'] = df['location'].apply(
                    lambda x: x.get('pincode', None) if isinstance(x, dict) else None
                )
            except Exception:
                pass
                
        # Extract application details
        if 'application_details' in df.columns:
            try:
                # Extract application date
                df['application_date'] = df['application_details'].apply(
                    lambda x: pd.to_datetime(x.get('application_date', None)) 
                    if isinstance(x, dict) and x.get('application_date') is not None 
                    else None
                )
                
                # Extract processing time
                df['processing_time'] = df['application_details'].apply(
                    lambda x: x.get('processing_time_days', None) if isinstance(x, dict) else None
                )
                
                # Extract rejection reason
                df['rejection_reason'] = df['application_details'].apply(
                    lambda x: x.get('rejection_reason', None) if isinstance(x, dict) else None
                )
            except Exception:
                pass
        
        return df
    
    def _preprocess_agents_data(self, df):
        """
        Preprocess agent data.
        
        Args:
            df: DataFrame with agent data
            
        Returns:
            Preprocessed DataFrame
        """
        if df is None or len(df) == 0:
            return df
            
        # Convert joining date to datetime
        if 'joining_date' in df.columns:
            try:
                df['joining_date'] = pd.to_datetime(df['joining_date'])
            except Exception:
                pass
                
        return df
    
    def _connect_to_mongodb(self):
        """
        Connect to MongoDB.
        
        Returns:
            True if connection successful, False otherwise
        """
        # Return cached connection status if available
        if self._db_connection:
            return True
            
        # Try to connect to MongoDB
        try:
            self._mongo_client = MongoClient(self.db_uri, serverSelectionTimeoutMS=5000)
            self._mongo_client.server_info()  # Force connection to verify
            self._db_connection = True
            return True
        except Exception as e:
            # print(f"Error connecting to MongoDB: {str(e)}")
            self._db_connection = False
            return False
    
    def _json_serial(self, obj):
        """
        JSON serializer for objects not serializable by default json code.
        
        Args:
            obj: Object to serialize
            
        Returns:
            Serialized object
        """
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
