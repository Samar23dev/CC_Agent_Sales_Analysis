"""
GroMo AI Sales Coach - Agent Service

This module provides services for analyzing agent performance,
generating insights, and creating agent dashboards.
"""

import pandas as pd
import numpy as np
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns

from data.data_loader import DataLoader
from utils.metrics import calculate_success_rate, calculate_avg_commission
from utils.visualization import (
    create_monthly_trend_chart, 
    create_card_performance_chart, 
    create_segment_performance_chart
)


class AgentService:
    """Service for agent-related operations."""
    
    def __init__(self):
        """Initialize the Agent Service."""
        self.data_loader = DataLoader()
    
    def analyze_performance(self, agent_id):
        """
        Analyze performance metrics for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with agent performance metrics
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        agents_data = self.data_loader.load_agents_data()
        cards_data = self.data_loader.load_cards_data()
        
        if sales_data is None:
            return None
        
        # Filter data for the specific agent
        agent_sales = sales_data[sales_data['agent_id'] == agent_id].copy()
        
        if len(agent_sales) == 0:
            return None
            
        # Get agent info if available
        agent_info = None
        if agents_data is not None:
            agent_row = agents_data[agents_data['agent_id'] == agent_id]
            if len(agent_row) > 0:
                agent_info = agent_row.iloc[0].to_dict()
        
        # Calculate overall performance metrics
        total_sales = len(agent_sales)
        successful_sales = agent_sales['success_flag'].sum() if 'success_flag' in agent_sales.columns else 0
        success_rate = calculate_success_rate(successful_sales, total_sales)
        total_commission = agent_sales['commission'].sum() if 'commission' in agent_sales.columns else 0
        avg_commission = calculate_avg_commission(total_commission, successful_sales)
        
        # Calculate performance by card
        if 'card_id' in agent_sales.columns:
            card_performance = agent_sales.groupby('card_id').agg({
                'sale_id': 'count',
                'success_flag': 'sum',
                'commission': 'sum'
            }).reset_index()
            
            card_performance = card_performance.rename(columns={
                'sale_id': 'total_sales',
                'success_flag': 'successful_sales'
            })
            
            card_performance['success_rate'] = card_performance.apply(
                lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                axis=1
            )
            
            card_performance['avg_commission'] = card_performance.apply(
                lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                axis=1
            )
            
            # Add card details if available
            if cards_data is not None:
                card_performance = card_performance.merge(
                    cards_data[['card_id', 'name', 'type']],
                    on='card_id',
                    how='left'
                )
            
            # Sort by total commission
            card_performance = card_performance.sort_values('commission', ascending=False)
            
            card_performance_list = card_performance.to_dict('records')
        else:
            card_performance_list = []
        
        # Calculate monthly performance if date information is available
        if 'date' in agent_sales.columns:
            agent_sales['month_year'] = pd.to_datetime(agent_sales['date']).dt.strftime('%Y-%m')
            
            monthly_performance = agent_sales.groupby('month_year').agg({
                'sale_id': 'count',
                'success_flag': 'sum',
                'commission': 'sum'
            }).reset_index()
            
            monthly_performance = monthly_performance.rename(columns={
                'sale_id': 'total_sales',
                'success_flag': 'successful_sales'
            })
            
            monthly_performance['success_rate'] = monthly_performance.apply(
                lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                axis=1
            )
            
            monthly_performance['avg_commission'] = monthly_performance.apply(
                lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                axis=1
            )
            
            # Sort by month_year
            monthly_performance['date'] = pd.to_datetime(monthly_performance['month_year'] + '-01')
            monthly_performance = monthly_performance.sort_values('date')
            
            monthly_performance_list = monthly_performance.to_dict('records')
        else:
            monthly_performance_list = []
        
        # Calculate performance by customer segment if customer data is available
        segment_performance_list = []
        
        if 'customer_details' in agent_sales.columns:
            # Extract customer income
            if 'customer_income' in agent_sales.columns:
                # Create income segments
                agent_sales['income_segment'] = pd.cut(
                    agent_sales['customer_income'],
                    bins=[0, 300000, 600000, 1000000, float('inf')],
                    labels=['Low', 'Medium', 'High', 'Very High']
                )
                
                segment_performance = agent_sales.groupby('income_segment').agg({
                    'sale_id': 'count',
                    'success_flag': 'sum',
                    'commission': 'sum'
                }).reset_index()
                
                segment_performance = segment_performance.rename(columns={
                    'sale_id': 'total_sales',
                    'success_flag': 'successful_sales'
                })
                
                segment_performance['success_rate'] = segment_performance.apply(
                    lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                    axis=1
                )
                
                segment_performance['avg_commission'] = segment_performance.apply(
                    lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                    axis=1
                )
                
                segment_performance_list = segment_performance.to_dict('records')
        
        # Build the result
        result = {
            'agent_info': agent_info,
            'overall': {
                'total_sales': total_sales,
                'successful_sales': successful_sales,
                'success_rate': success_rate,
                'total_commission': total_commission,
                'avg_commission': avg_commission
            },
            'card_performance': card_performance_list,
            'monthly_performance': monthly_performance_list,
            'segment_performance': segment_performance_list
        }
        
        return result
    
    def create_dashboard(self, agent_id):
        """
        Create a comprehensive dashboard for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with performance data and visualizations
        """
        # Get agent performance data
        performance = self.analyze_performance(agent_id)
        
        if performance is None:
            return None
        
        # Create visualizations
        charts = {}
        
        # Monthly trend chart
        if performance['monthly_performance']:
            try:
                monthly_df = pd.DataFrame(performance['monthly_performance'])
                fig = create_monthly_trend_chart(monthly_df)
                
                # Convert to base64 image
                img_data = BytesIO()
                fig.savefig(img_data, format='png', bbox_inches='tight')
                img_data.seek(0)
                img_base64 = base64.b64encode(img_data.read()).decode('utf-8')
                plt.close(fig)
                
                charts['monthly_trend'] = img_base64
            except Exception as e:
                print(f"Error creating monthly trend chart: {str(e)}")
        
        # Card performance chart
        if performance['card_performance']:
            try:
                card_df = pd.DataFrame(performance['card_performance'])
                fig = create_card_performance_chart(card_df)
                
                # Convert to base64 image
                img_data = BytesIO()
                fig.savefig(img_data, format='png', bbox_inches='tight')
                img_data.seek(0)
                img_base64 = base64.b64encode(img_data.read()).decode('utf-8')
                plt.close(fig)
                
                charts['card_performance'] = img_base64
            except Exception as e:
                print(f"Error creating card performance chart: {str(e)}")
        
        # Segment performance chart
        if performance['segment_performance']:
            try:
                segment_df = pd.DataFrame(performance['segment_performance'])
                fig = create_segment_performance_chart(segment_df, 'income_segment')
                
                # Convert to base64 image
                img_data = BytesIO()
                fig.savefig(img_data, format='png', bbox_inches='tight')
                img_data.seek(0)
                img_base64 = base64.b64encode(img_data.read()).decode('utf-8')
                plt.close(fig)
                
                charts['segment_performance'] = img_base64
            except Exception as e:
                print(f"Error creating segment performance chart: {str(e)}")
        
        # Generate insights
        insights = self.generate_insights(agent_id)
        
        # Build dashboard
        dashboard = {
            'performance': performance,
            'charts': charts,
            'insights': insights
        }
        
        return dashboard
    
    def generate_insights(self, agent_id):
        """
        Generate personalized insights for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with insights and recommendations
        """
        # Get agent performance data
        performance = self.analyze_performance(agent_id)
        
        if performance is None:
            return None
        
        # Load data for network-wide benchmarking
        sales_data = self.data_loader.load_sales_data()
        
        if sales_data is None:
            return None
        
        # Calculate network-wide metrics
        network_total_sales = len(sales_data)
        network_successful_sales = sales_data['success_flag'].sum() if 'success_flag' in sales_data.columns else 0
        network_success_rate = calculate_success_rate(network_successful_sales, network_total_sales)
        network_total_commission = sales_data['commission'].sum() if 'commission' in sales_data.columns else 0
        network_avg_commission = calculate_avg_commission(network_total_commission, network_successful_sales)
        
        # Generate insights
        strengths = []
        areas_for_improvement = []
        recommendations = []
        
        # Compare success rate with network average
        agent_success_rate = performance['overall']['success_rate']
        if agent_success_rate > network_success_rate + 0.05:
            strengths.append(
                f"Your approval rate of {agent_success_rate:.1%} is above the network average of {network_success_rate:.1%}, indicating strong customer qualification skills."
            )
        elif agent_success_rate < network_success_rate - 0.05:
            areas_for_improvement.append(
                f"Your approval rate of {agent_success_rate:.1%} is below the network average of {network_success_rate:.1%}. Better pre-screening of customers could improve this metric."
            )
        
        # Check average commission vs network
        agent_avg_commission = performance['overall']['avg_commission']
        if agent_avg_commission > network_avg_commission + 200:
            strengths.append(
                f"Your average commission of ₹{agent_avg_commission:.0f} is higher than the network average of ₹{network_avg_commission:.0f}, showing good focus on higher-value cards."
            )
        elif agent_avg_commission < network_avg_commission - 200:
            areas_for_improvement.append(
                f"Your average commission of ₹{agent_avg_commission:.0f} is below the network average of ₹{network_avg_commission:.0f}. Focusing on premium cards could increase your earnings."
            )
        
        # Analyze card mix
        card_performance = performance['card_performance']
        if card_performance:
            # Check if agent is too focused on a single card
            top_card = card_performance[0]
            top_card_share = top_card['total_sales'] / performance['overall']['total_sales']
            
            if top_card_share > 0.7 and len(card_performance) > 1:
                areas_for_improvement.append(
                    f"You're heavily focused on a single card type. Diversifying your product mix could increase your overall earnings."
                )
            
            # Find best performing cards to recommend
            best_cards = [
                card for card in card_performance 
                if card['success_rate'] >= 0.6 and 
                card['total_sales'] >= 3 and 
                card['avg_commission'] > agent_avg_commission
            ]
            
            if best_cards:
                for card in best_cards[:2]:
                    recommendations.append(
                        f"Increase focus on {card['name']}, which generates ₹{card['avg_commission']:.0f} average commission with {card['success_rate']:.1%} success rate."
                    )
            
            # Find poorly performing cards
            poor_cards = [
                card for card in card_performance 
                if card['success_rate'] < 0.4 and 
                card['total_sales'] >= 5
            ]
            
            if poor_cards:
                for card in poor_cards[:2]:
                    areas_for_improvement.append(
                        f"{card['name']} has a low approval rate of {card['success_rate']:.1%}. Consider improving customer qualification or focusing on other products."
                    )
        
        # Analyze monthly trends
        monthly_performance = performance['monthly_performance']
        if monthly_performance and len(monthly_performance) >= 2:
            # Check if the agent has a positive or negative trend
            recent_months = sorted(monthly_performance, key=lambda x: x['date'])[-3:]
            
            if recent_months[-1]['total_sales'] > recent_months[0]['total_sales'] * 1.1:
                strengths.append(
                    f"Your sales volume is growing, with {recent_months[-1]['total_sales']} applications in your most recent month compared to {recent_months[0]['total_sales']} three months ago."
                )
            elif recent_months[-1]['total_sales'] < recent_months[0]['total_sales'] * 0.9:
                areas_for_improvement.append(
                    f"Your sales volume has decreased from {recent_months[0]['total_sales']} applications three months ago to {recent_months[-1]['total_sales']} in your most recent month."
                )
        
        # Analyze segment performance
        segment_performance = performance['segment_performance']
        if segment_performance:
            # Find best performing segments
            best_segments = [
                segment for segment in segment_performance 
                if segment['success_rate'] >= 0.6 and 
                segment['total_sales'] >= 3
            ]
            
            if best_segments:
                best_segment = max(best_segments, key=lambda x: x['success_rate'])
                recommendations.append(
                    f"Focus on the {best_segment['income_segment']} income segment, where you have a {best_segment['success_rate']:.1%} approval rate."
                )
        
        # Add generic recommendations if needed
        if not recommendations:
            recommendations.append(
                "Use the AI Sales Coach tools to analyze each customer's profile before application to predict success probability."
            )
            recommendations.append(
                "Review the sales scripts for your most successful card types to refine your pitching approach."
            )
        
        # Build insights
        insights = {
            'strengths': strengths,
            'areas_for_improvement': areas_for_improvement,
            'recommendations': recommendations
        }
        
        return insights
