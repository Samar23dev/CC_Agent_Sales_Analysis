"""
GroMo AI Sales Coach - Agent Service

This module provides services for analyzing agent performance,
generating personalized insights, and creating agent dashboards.
"""

import os
from datetime import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
import io
import base64

from data.data_loader import DataLoader
from utils.metrics import calculate_success_rate, calculate_avg_commission
from utils.visualization import create_monthly_trend_chart, create_card_performance_chart
from config import Config


class AgentService:
    """Service for agent-related operations."""
    
    def __init__(self):
        """Initialize the Agent Service."""
        self.data_loader = DataLoader()
        self.output_dir = Config.OUTPUT_DIR
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def analyze_performance(self, agent_id):
        """
        Analyze agent performance metrics.
        
        Args:
            agent_id: ID of the agent to analyze
            
        Returns:
            Dictionary of performance metrics
        """
        # Load data
        sales_data = self.data_loader.load_sales_data()
        cards_data = self.data_loader.load_cards_data()
        agents_data = self.data_loader.load_agents_data()
        
        if sales_data is None or cards_data is None:
            return None
            
        # Filter data for specific agent
        agent_sales = sales_data[sales_data['agent_id'] == agent_id].copy()
        if len(agent_sales) == 0:
            return None
            
        # Get agent details
        agent_info = None
        if agents_data is not None:
            agent_row = agents_data[agents_data['agent_id'] == agent_id]
            if len(agent_row) > 0:
                agent_info = agent_row.iloc[0].to_dict()
        
        # Calculate overall metrics
        total_sales = len(agent_sales)
        successful_sales = agent_sales['success_flag'].sum() if 'success_flag' in agent_sales.columns else 0
        success_rate = calculate_success_rate(successful_sales, total_sales)
        total_commission = agent_sales['commission'].sum() if 'commission' in agent_sales.columns else 0
        avg_commission = calculate_avg_commission(total_commission, successful_sales)
        
        # Calculate card performance
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
        
        # Add card details
        if cards_data is not None:
            card_performance = card_performance.merge(cards_data, on='card_id', how='left')
            
        # Calculate monthly performance
        if 'date' in agent_sales.columns:
            agent_sales['month_year'] = agent_sales['date'].dt.strftime('%Y-%m')
            
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
            
            # Sort by month-year
            monthly_performance = monthly_performance.sort_values('month_year')
        else:
            monthly_performance = None
        
        # Calculate customer segment performance
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
        else:
            segment_performance = None
            
        # Calculate employment type performance
        if 'customer_employment' in agent_sales.columns:
            employment_performance = agent_sales.groupby('customer_employment').agg({
                'sale_id': 'count',
                'success_flag': 'sum',
                'commission': 'sum'
            }).reset_index()
            
            employment_performance = employment_performance.rename(columns={
                'sale_id': 'total_sales',
                'success_flag': 'successful_sales'
            })
            
            employment_performance['success_rate'] = employment_performance.apply(
                lambda row: calculate_success_rate(row['successful_sales'], row['total_sales']),
                axis=1
            )
            
            employment_performance['avg_commission'] = employment_performance.apply(
                lambda row: calculate_avg_commission(row['commission'], row['successful_sales']),
                axis=1
            )
        else:
            employment_performance = None
            
        # Compile results
        results = {
            'agent_info': agent_info,
            'overall': {
                'total_sales': total_sales,
                'successful_sales': successful_sales,
                'success_rate': success_rate,
                'total_commission': total_commission,
                'avg_commission': avg_commission
            },
            'card_performance': card_performance.to_dict('records') if len(card_performance) > 0 else [],
            'monthly_performance': monthly_performance.to_dict('records') if monthly_performance is not None and len(monthly_performance) > 0 else [],
            'segment_performance': segment_performance.to_dict('records') if segment_performance is not None and len(segment_performance) > 0 else [],
            'employment_performance': employment_performance.to_dict('records') if employment_performance is not None and len(employment_performance) > 0 else []
        }
        
        return results
    
    def create_dashboard(self, agent_id):
        """
        Create a comprehensive dashboard for a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dictionary with dashboard data and charts
        """
        # Get performance metrics
        performance = self.analyze_performance(agent_id)
        if not performance:
            return None
        
        # Generate visualizations
        charts = {}
        
        # Monthly performance chart
        if performance['monthly_performance']:
            monthly_df = pd.DataFrame(performance['monthly_performance'])
            if len(monthly_df) > 1:
                monthly_chart = create_monthly_trend_chart(monthly_df)
                charts['monthly_trend'] = self._fig_to_base64(monthly_chart)
        
        # Card performance chart
        if performance['card_performance']:
            card_df = pd.DataFrame(performance['card_performance'])
            if len(card_df) > 0:
                card_chart = create_card_performance_chart(card_df)
                charts['card_performance'] = self._fig_to_base64(card_chart)
        
        # Segment performance chart
        if performance['segment_performance']:
            segment_df = pd.DataFrame(performance['segment_performance'])
            if len(segment_df) > 0:
                segment_chart = self._create_segment_chart(segment_df)
                charts['segment_performance'] = self._fig_to_base64(segment_chart)
        
        # Generate insights
        insights = self.generate_insights(agent_id, performance)
        
        # Create dashboard data
        dashboard = {
            'performance': performance,
            'charts': charts,
            'insights': insights
        }
        
        return dashboard
    
    def generate_insights(self, agent_id, performance=None):
        """
        Generate personalized insights for an agent.
        
        Args:
            agent_id: ID of the agent
            performance: Performance data (optional, will be loaded if not provided)
            
        Returns:
            Dictionary with insights and recommendations
        """
        if not performance:
            performance = self.analyze_performance(agent_id)
            if not performance:
                return None
        
        # Get overall performance metrics
        overall = performance['overall']
        success_rate = overall['success_rate']
        avg_commission = overall['avg_commission']
        
        # Load sales data for benchmarking
        sales_data = self.data_loader.load_sales_data()
        if sales_data is None:
            return None
            
        # Calculate benchmark metrics
        avg_success_rate = sales_data['success_flag'].mean() if 'success_flag' in sales_data.columns else 0
        avg_network_commission = (
            sales_data[sales_data['success_flag'] == True]['commission'].sum() / 
            sales_data['success_flag'].sum()
        ) if 'success_flag' in sales_data.columns and 'commission' in sales_data.columns else 0
        
        # Generate insights
        insights = {
            'strengths': [],
            'areas_for_improvement': [],
            'recommendations': []
        }
        
        # Analyze strengths
        if success_rate > avg_success_rate * 1.1:  # At least 10% better than average
            insights['strengths'].append(
                f"Your approval rate of {success_rate:.1%} is above the network average of {avg_success_rate:.1%}, " 
                "indicating strong customer qualification skills."
            )
            
        if avg_commission > avg_network_commission * 1.1:  # At least 10% better than average
            insights['strengths'].append(
                f"Your average commission of ₹{avg_commission:.0f} exceeds the network average of " 
                f"₹{avg_network_commission:.0f}, showing good focus on higher-value products."
            )
        
        # Identify best performing card
        if performance['card_performance']:
            card_df = pd.DataFrame(performance['card_performance'])
            if len(card_df) > 0:
                # Get card with highest total commission
                best_card = card_df.loc[card_df['commission'].idxmax()]
                card_name = best_card.get('name', best_card['card_id'])
                insights['strengths'].append(
                    f"You excel at selling {card_name}, which has generated "
                    f"₹{best_card['commission']:.0f} in commissions with a "
                    f"{best_card['success_rate']:.1%} success rate."
                )
        
        # Identify best customer segment
        if performance['segment_performance']:
            segment_df = pd.DataFrame(performance['segment_performance'])
            if len(segment_df) > 0:
                # Get segment with highest success rate (min 3 sales)
                best_segment = segment_df[segment_df['total_sales'] >= 3].sort_values('success_rate', ascending=False)
                if len(best_segment) > 0:
                    best_segment = best_segment.iloc[0]
                    insights['strengths'].append(
                        f"You perform particularly well with {best_segment['income_segment']} income customers, "
                        f"achieving a {best_segment['success_rate']:.1%} success rate."
                    )
        
        # Analyze areas for improvement
        if success_rate < avg_success_rate * 0.9:  # At least 10% worse than average
            insights['areas_for_improvement'].append(
                f"Your approval rate of {success_rate:.1%} is below the network average of {avg_success_rate:.1%}. "
                "Consider improving customer qualification before application."
            )
            
        if avg_commission < avg_network_commission * 0.9:  # At least 10% worse than average
            insights['areas_for_improvement'].append(
                f"Your average commission of ₹{avg_commission:.0f} is below the network average of "
                f"₹{avg_network_commission:.0f}. Consider focusing on higher-value products."
            )
        
        # Analyze product mix
        if performance['card_performance']:
            card_df = pd.DataFrame(performance['card_performance'])
            if len(card_df) > 0:
                # Check if agent is focusing too much on one card
                top_card_sales = card_df.iloc[0]['total_sales'] if len(card_df) > 0 else 0
                total_sales = overall['total_sales']
                
                if top_card_sales / total_sales > 0.7 and len(card_df) > 1:
                    insights['areas_for_improvement'].append(
                        "You're heavily focused on a single card type. Diversifying your product mix "
                        "could increase your overall earnings."
                    )
                
                # Check for low success rate cards with high volume
                problem_cards = card_df[(card_df['success_rate'] < 0.4) & (card_df['total_sales'] > 5)]
                if len(problem_cards) > 0:
                    for _, card in problem_cards.iterrows():
                        card_name = card.get('name', card['card_id'])
                        insights['areas_for_improvement'].append(
                            f"Your success rate for {card_name} is only {card['success_rate']:.1%} despite "
                            f"{card['total_sales']} applications. Consider better qualifying customers for this card."
                        )
        
        # Generate recommendations
        # Recommend improving success rate if below 70%
        if success_rate < 0.7:
            insights['recommendations'].append(
                "Improve your approval rate by better qualifying customers before application. "
                "Verify income documents and credit history before submitting applications."
            )
        
        # Recommend focusing on high-value cards
        if performance['card_performance']:
            card_df = pd.DataFrame(performance['card_performance'])
            if len(card_df) > 0:
                # Find cards with high commission but low volume
                high_value_cards = card_df.sort_values('avg_commission', ascending=False).head(3)
                for _, card in high_value_cards.iterrows():
                    if card['total_sales'] < total_sales * 0.2:  # Less than 20% of total sales
                        card_name = card.get('name', card['card_id'])
                        insights['recommendations'].append(
                            f"Increase focus on {card_name}, which generates ₹{card['avg_commission']:.0f} "
                            f"average commission with {card['success_rate']:.1%} success rate."
                        )
        
        # Recommend targeting specific customer segments
        if performance['segment_performance']:
            segment_df = pd.DataFrame(performance['segment_performance'])
            if len(segment_df) > 0:
                # Find segments with high commission and success rate
                high_value_segments = segment_df.sort_values('avg_commission', ascending=False).head(2)
                for _, segment in high_value_segments.iterrows():
                    if segment['success_rate'] > 0.5:  # At least 50% success rate
                        insights['recommendations'].append(
                            f"Prioritize {segment['income_segment']} income customers, who generate "
                            f"₹{segment['avg_commission']:.0f} average commission with a "
                            f"{segment['success_rate']:.1%} success rate."
                        )
        
        # Add general recommendations
        # For new agents (less than 10 sales)
        if overall['total_sales'] < 10:
            insights['recommendations'].append(
                "As a newer partner, focus on building experience with easier-to-sell products first. "
                "Try targeting family and friends to build confidence."
            )
        
        # For all agents
        insights['recommendations'].append(
            "Set clear monthly goals for applications and approvals. Tracking your progress can help "
            "you stay motivated and identify areas for improvement."
        )
        
        insights['recommendations'].append(
            "Use personalized sales scripts for each card type. Practice objection handling to "
            "increase your conversion rate."
        )
        
        return insights
    
    def _create_segment_chart(self, segment_df):
        """
        Create a chart showing performance by customer segment.
        
        Args:
            segment_df: DataFrame with segment performance data
            
        Returns:
            Matplotlib figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Sort by segment ordinal
        segment_order = ['Low', 'Medium', 'High', 'Very High']
        segment_df['order'] = segment_df['income_segment'].apply(lambda x: segment_order.index(x) if x in segment_order else -1)
        segment_df = segment_df.sort_values('order')
        
        # Plot success rate by segment
        ax1.bar(segment_df['income_segment'], segment_df['success_rate'], color='blue')
        ax1.set_title('Success Rate by Income Segment')
        ax1.set_ylim(0, 1)
        ax1.grid(axis='y')
        
        # Add percentage labels
        for i, v in enumerate(segment_df['success_rate']):
            ax1.text(i, v + 0.05, f"{v:.1%}", ha='center')
        
        # Plot average commission by segment
        ax2.bar(segment_df['income_segment'], segment_df['avg_commission'], color='green')
        ax2.set_title('Avg. Commission by Income Segment')
        ax2.grid(axis='y')
        
        # Add value labels
        for i, v in enumerate(segment_df['avg_commission']):
            ax2.text(i, v + 100, f"₹{v:.0f}", ha='center')
        
        plt.tight_layout()
        return fig
    
    def _fig_to_base64(self, fig):
        """
        Convert a matplotlib figure to a base64 encoded string.
        
        Args:
            fig: Matplotlib figure object
            
        Returns:
            Base64 encoded string
        """
        # Save figure to a bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        
        # Encode as base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        # Close the figure to free memory
        plt.close(fig)
        
        return img_str
