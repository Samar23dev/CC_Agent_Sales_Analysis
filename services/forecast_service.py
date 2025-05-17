"""
GroMo AI Sales Coach - Forecast Service

This module provides services for forecasting commission
and generating optimization suggestions for agents.
"""

from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from data.data_loader import DataLoader
from utils.metrics import calculate_success_rate, calculate_avg_commission


class ForecastService:
    """Service for forecast-related operations."""
    
    def __init__(self):
        """Initialize the Forecast Service."""
        self.data_loader = DataLoader()
    
    def generate_forecast(self, agent_id, forecast_months=6):
        """
        Generate a commission forecast for a specific agent.
        
        Args:
            agent_id: ID of the agent
            forecast_months: Number of months to forecast
            
        Returns:
            Dictionary with forecast data and optimization suggestions
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        agents_data = self.data_loader.load_agents_data()
        
        if sales_data is None:
            return None
        
        # Filter data for the specific agent
        agent_sales = sales_data[sales_data['agent_id'] == agent_id].copy()
        
        # Get agent info if available
        agent_info = None
        if agents_data is not None:
            agent_row = agents_data[agents_data['agent_id'] == agent_id]
            if len(agent_row) > 0:
                agent_info = agent_row.iloc[0].to_dict()
        
        # If no sales data found, return a basic forecast for new agents
        if len(agent_sales) == 0:
            return self._generate_new_agent_forecast(agent_id, forecast_months, agent_info)
        
        # Extract month and year from date
        if 'date' in agent_sales.columns:
            agent_sales['month_year'] = agent_sales['date'].dt.strftime('%Y-%m')
            
            # Calculate monthly performance
            monthly = agent_sales.groupby('month_year').agg({
                'sale_id': 'count',
                'success_flag': 'sum',
                'commission': 'sum'
            }).reset_index()
            
            monthly = monthly.rename(columns={
                'sale_id': 'total_sales',
                'success_flag': 'successful_sales'
            })
            
            monthly['success_rate'] = monthly.apply(
                lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                axis=1
            )
            
            monthly['avg_commission'] = monthly.apply(
                lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                axis=1
            )
            
            # Convert month_year to datetime for sorting
            monthly['date'] = pd.to_datetime(monthly['month_year'] + '-01')
            monthly = monthly.sort_values('date')
            
            # Calculate trends for forecasting
            if len(monthly) >= 2:
                # Calculate growth rates between consecutive months
                monthly['prev_sales'] = monthly['total_sales'].shift(1)
                monthly['sales_growth'] = (monthly['total_sales'] - monthly['prev_sales']) / monthly['prev_sales'].replace(0, 1)
                
                # Remove extreme outliers
                growth_rates = monthly['sales_growth'].dropna()
                growth_rates = growth_rates[growth_rates.between(growth_rates.quantile(0.05), growth_rates.quantile(0.95))]
                
                # Calculate average growth rate
                avg_growth_rate = growth_rates.mean() if len(growth_rates) > 0 else 0.05  # Default to 5% if no valid data
                
                # Calculate average success rate (more weight to recent months)
                weights = np.linspace(0.5, 1.0, len(monthly))
                weighted_success_rates = monthly['success_rate'] * weights
                avg_success_rate = weighted_success_rates.sum() / weights.sum() if len(weighted_success_rates) > 0 else 0.5
                
                # Calculate average commission per successful sale
                weighted_commissions = monthly['avg_commission'] * weights
                avg_commission = weighted_commissions.sum() / weights.sum() if len(weighted_commissions) > 0 else 1000
                
                # Generate forecast
                forecast_data = self._generate_forecast_data(
                    monthly.iloc[-1], 
                    avg_growth_rate, 
                    avg_success_rate, 
                    avg_commission, 
                    forecast_months
                )
                
                # Generate summary
                summary = {
                    'forecast_months': forecast_months,
                    'total_forecast_sales': sum(month['total_sales'] for month in forecast_data),
                    'total_forecast_commission': sum(month['commission'] for month in forecast_data),
                    'avg_monthly_commission': sum(month['commission'] for month in forecast_data) / forecast_months,
                    'projected_growth': avg_growth_rate
                }
                
                # Generate optimization suggestions
                optimization = self.get_optimization_suggestions(
                    agent_id, avg_growth_rate, avg_success_rate, avg_commission
                )
                
                return {
                    'agent_info': agent_info,
                    'historical': monthly[['month_year', 'total_sales', 'successful_sales', 'success_rate', 'commission', 'avg_commission']].to_dict('records'),
                    'forecast': forecast_data,
                    'summary': summary,
                    'optimization': optimization
                }
            else:
                # Not enough historical data for trend analysis
                return self._generate_new_agent_forecast(agent_id, forecast_months, agent_info)
        else:
            # No date information in sales data
            return None
    
    def get_optimization_suggestions(self, agent_id, sales_growth=None, success_rate=None, avg_commission=None):
        """
        Generate optimization suggestions for an agent.
        
        Args:
            agent_id: ID of the agent
            sales_growth: Current sales growth rate (optional)
            success_rate: Current success rate (optional)
            avg_commission: Current average commission (optional)
            
        Returns:
            List of optimization suggestions
        """
        # Load data if parameters not provided
        if sales_growth is None or success_rate is None or avg_commission is None:
            sales_data = self.data_loader.load_sales_data()
            
            if sales_data is None:
                return []
            
            # Filter data for the specific agent
            agent_sales = sales_data[sales_data['agent_id'] == agent_id].copy()
            
            if len(agent_sales) == 0:
                # New agent - use default values
                sales_growth = 0.05  # 5% monthly growth
                success_rate = 0.5   # 50% success rate
                avg_commission = 1000  # ₹1000 per successful sale
            else:
                # Calculate metrics from sales data
                total_sales = len(agent_sales)
                successful_sales = agent_sales['success_flag'].sum() if 'success_flag' in agent_sales.columns else 0
                success_rate = calculate_success_rate(successful_sales, total_sales)
                total_commission = agent_sales['commission'].sum() if 'commission' in agent_sales.columns else 0
                avg_commission = calculate_avg_commission(total_commission, successful_sales)
                
                # Calculate sales growth if date information available
                if 'date' in agent_sales.columns:
                    agent_sales['month_year'] = agent_sales['date'].dt.strftime('%Y-%m')
                    monthly = agent_sales.groupby('month_year').size().reset_index(name='count')
                    
                    if len(monthly) >= 2:
                        monthly['prev_count'] = monthly['count'].shift(1)
                        monthly['growth'] = (monthly['count'] - monthly['prev_count']) / monthly['prev_count'].replace(0, 1)
                        sales_growth = monthly['growth'].mean()
                    else:
                        sales_growth = 0.05  # Default to 5% if not enough data
                else:
                    sales_growth = 0.05  # Default to 5% if no date information
        
        # Generate suggestions based on metrics
        suggestions = []
        
        # Suggest improving success rate if below 70%
        if success_rate < 0.7:
            suggestions.append({
                'category': 'Improve Approval Rate',
                'description': f"Your current approval rate of {success_rate:.1%} can be improved. Better pre-screening of customers can increase this to 70-80%.",
                'impact': "Increasing your approval rate to 70% could boost your monthly commission by approximately 20%.",
                'action_items': [
                    "Pre-check customer credit scores before application",
                    "Verify income documents thoroughly",
                    "Match customers with cards they're most likely to qualify for",
                    "Use the AI Success Predictor tool before submitting applications"
                ]
            })
            
        # Suggest increasing sales volume if growth rate is low
        if sales_growth < 0.1:  # Less than 10% monthly growth
            suggestions.append({
                'category': 'Increase Sales Volume',
                'description': f"Your current monthly growth rate of {sales_growth:.1%} is relatively low. Increasing your prospecting activities can accelerate growth.",
                'impact': "Increasing your monthly applications by 20% could lead to a corresponding increase in commission.",
                'action_items': [
                    "Set a daily target for new lead contacts",
                    "Use the AI Lead Recommender to identify high-potential customers",
                    "Follow up with past customers for referrals",
                    "Explore untapped customer segments in your network"
                ]
            })
            
        # Suggest focusing on higher-commission products
        if avg_commission < 2000:  # Below average commission
            suggestions.append({
                'category': 'Optimize Product Mix',
                'description': "You can increase your average commission by focusing on higher-value cards.",
                'impact': f"Increasing your average commission from ₹{avg_commission:.0f} to ₹2,500 could boost your earnings by 25% or more.",
                'action_items': [
                    "Prioritize premium cards with higher commission rates",
                    "Look for cards with joining fee waiver offers to boost approval rates",
                    "Focus on customers with higher income levels who qualify for premium cards",
                    "Use the AI Card Recommender to identify the highest-commission cards for your customer base"
                ]
            })
            
        # Suggest personalized scripts and objection handling
        suggestions.append({
            'category': 'Enhance Sales Technique',
            'description': "Refine your sales approach to increase conversion rates.",
            'impact': "Effective sales techniques can boost both your sales volume and approval rate.",
            'action_items': [
                "Use personalized sales scripts for each card type",
                "Practice objection handling for common customer concerns",
                "Focus on card benefits most relevant to each customer",
                "Proactively address potential rejection reasons before submission"
            ]
        })
        
        # Suggest data-driven approach
        suggestions.append({
            'category': 'Use Data-Driven Insights',
            'description': "Let AI help you identify the best opportunities.",
            'impact': "Data-driven sales strategies can increase your efficiency and earnings.",
            'action_items': [
                "Review your performance dashboard weekly to track progress",
                "Use the Lead Recommender to prioritize high-probability prospects",
                "Check Success Predictor scores before submitting applications",
                "Experiment with different card types and customer segments to find your sweet spot"
            ]
        })
        
        return suggestions
    
    def _generate_forecast_data(self, last_month, growth_rate, success_rate, avg_commission, forecast_months):
        """
        Generate forecast data for future months.
        
        Args:
            last_month: Last month's performance data
            growth_rate: Monthly growth rate for total sales
            success_rate: Expected success rate
            avg_commission: Expected average commission per successful sale
            forecast_months: Number of months to forecast
            
        Returns:
            List of forecast data for each month
        """
        forecast = []
        
        # Start with last month's total sales
        prev_sales = last_month['total_sales']
        
        # Convert last_month's date to datetime if it's a string
        if isinstance(last_month['date'], str):
            last_date = pd.to_datetime(last_month['date'])
        else:
            last_date = last_month['date']
        
        # Cap growth rate at reasonable limits
        growth_rate = max(-0.1, min(growth_rate, 0.3))  # Between -10% and 30%
        
        # Generate forecast for each month
        for i in range(1, forecast_months + 1):
            # Calculate next month's date
            next_date = last_date + pd.DateOffset(months=i)
            month_str = next_date.strftime('%B %Y')
            
            # Forecast sales with growth rate
            # Add small random variation around the trend
            variation = np.random.normal(0, 0.05)  # Normal distribution with std dev of 5%
            adjusted_growth = growth_rate + variation
            adjusted_growth = max(-0.15, min(adjusted_growth, 0.35))  # Keep within reasonable bounds
            
            # Forecast total sales
            total_sales = max(1, round(prev_sales * (1 + adjusted_growth)))
            
            # Forecast successful sales
            successful_sales = round(total_sales * success_rate)
            
            # Forecast commission
            commission = successful_sales * avg_commission
            
            # Calculate cumulative commission (sum of all previous months plus this month)
            cumulative_commission = sum(month['commission'] for month in forecast) + commission
            
            # Create forecast record
            forecast.append({
                'month': month_str,
                'total_sales': total_sales,
                'successful_sales': successful_sales,
                'success_rate': success_rate,
                'commission': commission,
                'cumulative_commission': cumulative_commission
            })
            
            # Update prev_sales for next iteration
            prev_sales = total_sales
        
        return forecast
    
    def _generate_new_agent_forecast(self, agent_id, forecast_months, agent_info=None):
        """
        Generate a forecast for a new agent with no sales history.
        
        Args:
            agent_id: ID of the agent
            forecast_months: Number of months to forecast
            agent_info: Agent information (optional)
            
        Returns:
            Dictionary with forecast data
        """
        # Load network-wide data for benchmarking
        sales_data = self.data_loader.load_sales_data()
        
        if sales_data is None:
            # Use default values if no data available
            avg_first_month_sales = 5
            avg_success_rate = 0.5
            avg_commission = 1000
        else:
            # Calculate network averages
            avg_success_rate = sales_data['success_flag'].mean() if 'success_flag' in sales_data.columns else 0.5
            successful_sales = sales_data[sales_data['success_flag'] == True]
            avg_commission = successful_sales['commission'].mean() if len(successful_sales) > 0 else 1000
            
            # Try to estimate first month sales for new agents
            if 'date' in sales_data.columns and 'agent_id' in sales_data.columns:
                # For each agent, find their first month sales count
                sales_data['month_year'] = sales_data['date'].dt.strftime('%Y-%m')
                first_months = []
                
                for aid, group in sales_data.groupby('agent_id'):
                    first_month = group.sort_values('date')['month_year'].iloc[0]
                    first_month_sales = group[group['month_year'] == first_month].shape[0]
                    first_months.append(first_month_sales)
                
                if first_months:
                    # Use median to avoid outliers
                    avg_first_month_sales = int(np.median(first_months))
                else:
                    avg_first_month_sales = 5
            else:
                avg_first_month_sales = 5
        
        # Generate forecast data
        forecast_data = []
        total_sales = avg_first_month_sales
        monthly_growth = 0.2  # Higher growth rate for new agents (20%)
        
        # Get current date
        current_date = datetime.now()
        
        for i in range(1, forecast_months + 1):
            # Calculate next month's date
            next_date = current_date + timedelta(days=32 * i)
            next_date = next_date.replace(day=1)  # First day of the month
            month_str = next_date.strftime('%B %Y')
            
            # Forecast successful sales
            successful_sales = round(total_sales * avg_success_rate)
            
            # Forecast commission
            commission = successful_sales * avg_commission
            
            # Calculate cumulative commission
            cumulative_commission = sum(month['commission'] for month in forecast_data) + commission
            
            # Create forecast record
            forecast_data.append({
                'month': month_str,
                'total_sales': total_sales,
                'successful_sales': successful_sales,
                'success_rate': avg_success_rate,
                'commission': commission,
                'cumulative_commission': cumulative_commission
            })
            
            # Update total_sales for next month with growth
            total_sales = max(1, round(total_sales * (1 + monthly_growth)))
            
            # Gradually reduce growth rate as months progress (stabilizing effect)
            monthly_growth = max(0.05, monthly_growth - 0.03)
        
        # Generate summary
        summary = {
            'forecast_months': forecast_months,
            'total_forecast_sales': sum(month['total_sales'] for month in forecast_data),
            'total_forecast_commission': sum(month['commission'] for month in forecast_data),
            'avg_monthly_commission': sum(month['commission'] for month in forecast_data) / forecast_months,
            'projected_growth': 0.2  # Initial growth rate
        }
        
        # Generate optimization suggestions for new agents
        optimization = [
            {
                'category': 'Build Strong Foundation',
                'description': "As a new partner, focus on building a solid foundation in your first few months.",
                'impact': "A strong start can accelerate your earnings trajectory and build momentum.",
                'action_items': [
                    "Complete all available training modules in the GroMo app",
                    "Start with easier-to-sell products to build confidence",
                    "Target family and friends as your first customers",
                    "Practice your pitch until you can deliver it naturally"
                ]
            },
            {
                'category': 'Use AI Tools from Day One',
                'description': "Leverage the AI Sales Coach to skip the learning curve.",
                'impact': "New partners who use AI tools typically reach profitability faster.",
                'action_items': [
                    "Use the Success Predictor before submitting any application",
                    "Follow leads suggested by the Lead Recommender",
                    "Use pre-generated sales scripts for each card type",
                    "Track your weekly performance to identify improvement areas early"
                ]
            },
            {
                'category': 'Set Achievable Goals',
                'description': "Set clear, measurable goals for your first three months.",
                'impact': "Goal-oriented agents typically outperform their peers by 30% or more.",
                'action_items': [
                    "Aim for at least 5 applications in your first month",
                    "Target a 50% approval rate from the beginning",
                    "Set a goal to learn one new product category each week",
                    "Challenge yourself to increase your sales by 20% each month"
                ]
            }
        ]
        
        return {
            'agent_info': agent_info,
            'historical': [],  # No historical data for new agents
            'forecast': forecast_data,
            'summary': summary,
            'optimization': optimization
        }
