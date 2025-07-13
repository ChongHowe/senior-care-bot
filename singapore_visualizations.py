# Singapore Senior Care Interactive Visualizations
# Two interactive dashboards for the capstone project

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import json

class SingaporeHealthDashboard:
    """
    Interactive Dashboard 1: Singapore Senior Health Overview
    Real-time monitoring of senior health patterns across Singapore
    """
    
    def __init__(self):
        self.singapore_districts = ['Central', 'East', 'North', 'North-East', 'West']
        self.health_conditions = ['Diabetes', 'Hypertension', 'Heart Disease', 'Stroke', 'Kidney Disease']
        
    def load_singapore_data(self):
        """Load Singapore health and demographics data"""
        try:
            # Load the datasets we created
            demographics = pd.read_csv('data/singapore/raw/singapore_demographics.csv')
            chronic_disease = pd.read_csv('data/singapore/raw/chronic_disease_prevalence.csv')
            polyclinic = pd.read_csv('data/singapore/raw/polyclinic_attendance.csv')
            hospital = pd.read_csv('data/singapore/raw/hospital_bed_occupancy.csv')
            
            return demographics, chronic_disease, polyclinic, hospital
        except FileNotFoundError:
            st.error("Please run singapore_data_setup.py first to generate the datasets!")
            return None, None, None, None
    
    def create_singapore_map_visualization(self, demographics_data):
        """Create interactive map of Singapore with senior population density"""
        
        # Singapore coordinates for major towns (simplified)
        singapore_coords = {
            'Ang Mo Kio': [1.369, 103.845],
            'Bedok': [1.324, 103.930],
            'Bishan': [1.351, 103.848],
            'Bukit Batok': [1.349, 103.749],
            'Bukit Merah': [1.277, 103.825],
            'Bukit Panjang': [1.378, 103.772],
            'Bukit Timah': [1.325, 103.791],
            'Central Area': [1.287, 103.851],
            'Choa Chu Kang': [1.385, 103.745],
            'Clementi': [1.315, 103.765],
            'Geylang': [1.314, 103.871],
            'Hougang': [1.361, 103.886],
            'Jurong East': [1.333, 103.742],
            'Jurong West': [1.340, 103.705],
            'Kallang/Whampoa': [1.308, 103.856],
            'Marine Parade': [1.302, 103.906],
            'Pasir Ris': [1.372, 103.949],
            'Punggol': [1.401, 103.902],
            'Queenstown': [1.294, 103.806],
            'Sembawang': [1.449, 103.820],
            'Sengkang': [1.391, 103.895],
            'Serangoon': [1.357, 103.873],
            'Tampines': [1.345, 103.944],
            'Toa Payoh': [1.334, 103.847],
            'Woodlands': [1.437, 103.786],
            'Yishun': [1.429, 103.835]
        }
        
        # Add coordinates to demographics data
        demographics_data['lat'] = demographics_data['town'].map(lambda x: singapore_coords.get(x, [1.35, 103.82])[0])
        demographics_data['lon'] = demographics_data['town'].map(lambda x: singapore_coords.get(x, [1.35, 103.82])[1])
        
        # Create scatter map
        fig = px.scatter_mapbox(
            demographics_data,
            lat='lat',
            lon='lon',
            size='senior_population_60plus',
            color='senior_percentage',
            hover_name='town',
            hover_data={
                'total_population': ':,',
                'senior_population_60plus': ':,',
                'senior_percentage': ':.1%',
                'seniors_living_alone_pct': ':.1%',
                'healthcare_facilities': True
            },
            color_continuous_scale='Reds',
            size_max=30,
            zoom=10,
            center={'lat': 1.35, 'lon': 103.82},
            mapbox_style='open-street-map',
            title='🇸🇬 Singapore Senior Population Distribution',
            height=600
        )
        
        fig.update_layout(
            font=dict(size=14),
            title_font_size=18,
            coloraxis_colorbar=dict(title="Senior Population %")
        )
        
        return fig
    
    def create_health_conditions_chart(self, chronic_disease_data):
        """Create chronic disease prevalence chart by district"""
        
        # Aggregate data by district and condition
        district_summary = chronic_disease_data.groupby(['district', 'condition'])['prevalence_rate'].mean().reset_index()
        
        fig = px.bar(
            district_summary,
            x='district',
            y='prevalence_rate',
            color='condition',
            title='🏥 Chronic Disease Prevalence by Singapore District',
            labels={
                'prevalence_rate': 'Prevalence Rate (%)',
                'district': 'Singapore District',
                'condition': 'Health Condition'
            },
            height=500
        )
        
        fig.update_layout(
            xaxis_tickangle=-45,
            font=dict(size=12),
            title_font_size=16,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        fig.update_traces(texttemplate='%{y:.1%}', textposition='outside')
        
        return fig
    
    def create_healthcare_utilization_chart(self, polyclinic_data, hospital_data):
        """Create healthcare utilization trends"""
        
        # Convert date columns
        polyclinic_data['date'] = pd.to_datetime(polyclinic_data['date'])
        hospital_data['date'] = pd.to_datetime(hospital_data['date'])
        
        # Monthly aggregation
        polyclinic_monthly = polyclinic_data.groupby(polyclinic_data['date'].dt.to_period('M')).agg({
            'total_attendance': 'sum',
            'elderly_attendance': 'sum'
        }).reset_index()
        polyclinic_monthly['date'] = polyclinic_monthly['date'].dt.to_timestamp()
        polyclinic_monthly['elderly_percentage'] = polyclinic_monthly['elderly_attendance'] / polyclinic_monthly['total_attendance']
        
        hospital_monthly = hospital_data.groupby(hospital_data['date'].dt.to_period('M')).agg({
            'occupancy_rate': 'mean',
            'elderly_patients_pct': 'mean'
        }).reset_index()
        hospital_monthly['date'] = hospital_monthly['date'].dt.to_timestamp()
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Polyclinic Attendance Trends',
                'Hospital Bed Occupancy',
                'Elderly Healthcare Utilization',
                'Seasonal Patterns'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Polyclinic trends
        fig.add_trace(
            go.Scatter(
                x=polyclinic_monthly['date'],
                y=polyclinic_monthly['total_attendance'],
                name='Total Attendance',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=polyclinic_monthly['date'],
                y=polyclinic_monthly['elderly_attendance'],
                name='Elderly Attendance',
                line=dict(color='red')
            ),
            row=1, col=1
        )
        
        # Hospital occupancy
        fig.add_trace(
            go.Scatter(
                x=hospital_monthly['date'],
                y=hospital_monthly['occupancy_rate'],
                name='Occupancy Rate',
                line=dict(color='green')
            ),
            row=1, col=2
        )
        
        # Elderly utilization percentage
        fig.add_trace(
            go.Scatter(
                x=polyclinic_monthly['date'],
                y=polyclinic_monthly['elderly_percentage'],
                name='Polyclinic Elderly %',
                line=dict(color='orange')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=hospital_monthly['date'],
                y=hospital_monthly['elderly_patients_pct'],
                name='Hospital Elderly %',
                line=dict(color='purple')
            ),
            row=2, col=1
        )
        
        # Seasonal heatmap
        polyclinic_data['month'] = polyclinic_data['date'].dt.month
        polyclinic_data['year'] = polyclinic_data['date'].dt.year
        seasonal_data = polyclinic_data.groupby(['year', 'month'])['elderly_attendance'].sum().reset_index()
        seasonal_pivot = seasonal_data.pivot(index='year', columns='month', values='elderly_attendance')
        
        fig.add_trace(
            go.Heatmap(
                z=seasonal_pivot.values,
                x=[f'Month {i}' for i in range(1, 13)],
                y=seasonal_pivot.index,
                colorscale='YlOrRd',
                name='Seasonal Pattern'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="🏥 Singapore Healthcare Utilization Dashboard",
            title_font_size=18,
            showlegend=True
        )
        
        return fig
    
    def create_dashboard(self):
        """Create the complete Singapore health dashboard"""
        
        st.set_page_config(page_title="Singapore Senior Health Dashboard", layout="wide")
        
        st.title("🇸🇬 Singapore Senior Care Health Dashboard")
        st.markdown("### Real-time monitoring of senior health patterns across Singapore")
        
        # Load data
        demographics, chronic_disease, polyclinic, hospital = self.load_singapore_data()
        
        if demographics is None:
            return
        
        # Sidebar filters
        st.sidebar.header("🔍 Filters")
        selected_districts = st.sidebar.multiselect(
            "Select Districts",
            self.singapore_districts,
            default=self.singapore_districts
        )
        
        selected_conditions = st.sidebar.multiselect(
            "Select Health Conditions",
            self.health_conditions,
            default=self.health_conditions
        )
        
        # Key metrics
        st.header("📊 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_seniors = demographics['senior_population_60plus'].sum()
            st.metric("Total Seniors (60+)", f"{total_seniors:,}")
        
        with col2:
            avg_senior_pct = demographics['senior_percentage'].mean()
            st.metric("Average Senior %", f"{avg_senior_pct:.1%}")
        
        with col3:
            living_alone_avg = demographics['seniors_living_alone_pct'].mean()
            st.metric("Living Alone %", f"{living_alone_avg:.1%}")
        
        with col4:
            total_healthcare = demographics['healthcare_facilities'].sum()
            st.metric("Healthcare Facilities", f"{total_healthcare}")
        
        # Visualizations
        st.header("🗺️ Geographic Distribution")
        map_fig = self.create_singapore_map_visualization(demographics)
        st.plotly_chart(map_fig, use_container_width=True)
        
        st.header("🏥 Health Conditions")
        filtered_chronic = chronic_disease[
            (chronic_disease['district'].isin(selected_districts)) &
            (chronic_disease['condition'].isin(selected_conditions))
        ]
        conditions_fig = self.create_health_conditions_chart(filtered_chronic)
        st.plotly_chart(conditions_fig, use_container_width=True)
        
        st.header("📈 Healthcare Utilization")
        utilization_fig = self.create_healthcare_utilization_chart(polyclinic, hospital)
        st.plotly_chart(utilization_fig, use_container_width=True)

class SingaporeBotAnalyticsDashboard:
    """
    Interactive Dashboard 2: Bot Performance and User Analytics
    Monitoring bot effectiveness and user engagement patterns
    """
    
    def __init__(self):
        self.load_bot_data()
        
    def load_bot_data(self):
        """Load bot activity and model prediction data"""
        try:
            self.singapore_data = pd.read_csv('data/singapore/processed/singapore_enhanced_bot_data.csv')
            # Create time series data for bot activity
            self.create_bot_activity_data()
        except FileNotFoundError:
            st.error("Please run the data setup scripts first!")
    
    def create_bot_activity_data(self):
        """Generate bot activity time series data"""
        
        # Generate daily bot interactions for the past 3 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        activity_data = []
        
        for date in dates:
            daily_stats = {
                'date': date,
                'total_users': len(self.singapore_data) + np.random.randint(-50, 50),
                'active_users': np.random.randint(150, 400),
                'medication_reminders_sent': np.random.randint(800, 1500),
                'medication_confirmations': np.random.randint(600, 1200),
                'family_notifications': np.random.randint(50, 150),
                'emergency_alerts': np.random.randint(0, 5),
                'health_check_ins': np.random.randint(200, 500),
                'fall_risk_alerts': np.random.randint(5, 20),
                'anomaly_detections': np.random.randint(10, 40),
                'polyclinic_appointments_booked': np.random.randint(20, 80),
                'user_satisfaction_score': np.random.normal(4.2, 0.3),  # 1-5 scale
                'response_time_seconds': np.random.normal(2.5, 0.8),
                'system_uptime_pct': np.random.normal(0.995, 0.01)  # 99.5% uptime
            }
            
            # Weekend patterns
            if date.weekday() >= 5:
                daily_stats['active_users'] *= 0.8
                daily_stats['medication_reminders_sent'] *= 0.9
                daily_stats['polyclinic_appointments_booked'] *= 0.3
            
            # Holiday/special events (Singapore national holidays)
            singapore_holidays = ['2024-01-01', '2024-02-10', '2024-02-12', '2024-03-29', 
                                '2024-04-10', '2024-05-01', '2024-05-22', '2024-06-17', 
                                '2024-08-09', '2024-10-31', '2024-12-25']
            
            if date.strftime('%Y-%m-%d') in singapore_holidays:
                daily_stats['active_users'] *= 0.6
                daily_stats['family_notifications'] *= 1.5  # More family contact on holidays
            
            activity_data.append(daily_stats)
        
        self.bot_activity = pd.DataFrame(activity_data)
    
    def create_bot_performance_overview(self):
        """Create bot performance overview charts"""
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                'Daily Active Users',
                'Medication Adherence',
                'Emergency Response',
                'User Satisfaction',
                'System Performance',
                'Bot Feature Usage'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}, {"type": "pie"}]]
        )
        
        # Daily active users
        fig.add_trace(
            go.Scatter(
                x=self.bot_activity['date'],
                y=self.bot_activity['active_users'],
                name='Active Users',
                line=dict(color='blue'),
                fill='tonexty'
            ),
            row=1, col=1
        )
        
        # Medication adherence rate
        self.bot_activity['adherence_rate'] = (
            self.bot_activity['medication_confirmations'] / 
            self.bot_activity['medication_reminders_sent']
        )
        
        fig.add_trace(
            go.Scatter(
                x=self.bot_activity['date'],
                y=self.bot_activity['adherence_rate'],
                name='Adherence Rate',
                line=dict(color='green')
            ),
            row=1, col=2
        )
        
        # Emergency alerts
        fig.add_trace(
            go.Bar(
                x=self.bot_activity['date'],
                y=self.bot_activity['emergency_alerts'],
                name='Emergency Alerts',
                marker_color='red'
            ),
            row=1, col=3
        )
        
        # User satisfaction over time
        fig.add_trace(
            go.Scatter(
                x=self.bot_activity['date'],
                y=self.bot_activity['user_satisfaction_score'],
                name='Satisfaction Score',
                line=dict(color='orange'),
                mode='lines+markers'
            ),
            row=2, col=1
        )
        
        # System uptime
        fig.add_trace(
            go.Scatter(
                x=self.bot_activity['date'],
                y=self.bot_activity['system_uptime_pct'],
                name='System Uptime',
                line=dict(color='purple'),
                fill='tonexty'
            ),
            row=2, col=2
        )
        
        # Feature usage pie chart
        feature_usage = {
            'Medication Reminders': self.bot_activity['medication_reminders_sent'].sum(),
            'Health Check-ins': self.bot_activity['health_check_ins'].sum(),
            'Family Notifications': self.bot_activity['family_notifications'].sum(),
            'Appointment Booking': self.bot_activity['polyclinic_appointments_booked'].sum(),
            'Emergency Alerts': self.bot_activity['emergency_alerts'].sum()
        }
        
        fig.add_trace(
            go.Pie(
                labels=list(feature_usage.keys()),
                values=list(feature_usage.values()),
                name="Feature Usage"
            ),
            row=2, col=3
        )
        
        fig.update_layout(
            height=800,
            title_text="🤖 Singapore Senior Care Bot Analytics Dashboard",
            title_font_size=18,
            showlegend=True
        )
        
        return fig
    
    def create_user_demographics_analysis(self):
        """Analyze user demographics and usage patterns"""
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Users by HDB Flat Type',
                'Language Preferences',
                'Technology Comfort Levels',
                'Healthcare Subsidy Distribution'
            ),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "histogram"}, {"type": "bar"}]]
        )
        
        # HDB flat type distribution
        hdb_counts = self.singapore_data['hdb_flat_type'].value_counts()
        fig.add_trace(
            go.Bar(
                x=hdb_counts.index,
                y=hdb_counts.values,
                name='HDB Flat Types',
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # Language preferences pie chart
        lang_counts = self.singapore_data['preferred_language'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=lang_counts.index,
                values=lang_counts.values,
                name="Languages"
            ),
            row=1, col=2
        )
        
        # Technology comfort histogram
        fig.add_trace(
            go.Histogram(
                x=self.singapore_data['technology_comfort'],
                name='Tech Comfort',
                marker_color='green',
                nbinsx=5
            ),
            row=2, col=1
        )
        
        # Healthcare subsidy eligibility
        subsidy_counts = self.singapore_data['healthcare_subsidy_eligible'].value_counts()
        subsidy_labels = ['Not Eligible', 'Eligible']
        fig.add_trace(
            go.Bar(
                x=subsidy_labels,
                y=[subsidy_counts.get(0, 0), subsidy_counts.get(1, 0)],
                name='Subsidy Eligibility',
                marker_color='orange'
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=700,
            title_text="👥 User Demographics Analysis",
            title_font_size=16
        )
        
        return fig
    
    def create_ml_model_performance(self):
        """Display ML model performance metrics"""
        
        # Simulate model performance data
        model_metrics = {
            'Medication Adherence': {
                'accuracy': 0.87,
                'precision': 0.85,
                'recall': 0.89,
                'f1_score': 0.87,
                'predictions_today': 234
            },
            'Fall Risk Assessment': {
                'r2_score': 0.82,
                'rmse': 12.5,
                'mae': 9.8,
                'predictions_today': 156
            },
            'Health Anomaly Detection': {
                'accuracy': 0.91,
                'precision': 0.88,
                'recall': 0.85,
                'f1_score': 0.86,
                'anomalies_detected_today': 23
            }
        }
        
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Medication Adherence', 'Fall Risk Assessment', 'Anomaly Detection'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Medication adherence model
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=model_metrics['Medication Adherence']['accuracy'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Accuracy"},
                delta={'reference': 0.8},
                gauge={
                    'axis': {'range': [None, 1]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 0.7], 'color': "lightgray"},
                        {'range': [0.7, 0.9], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.9
                    }
                }
            ),
            row=1, col=1
        )
        
        # Fall risk model
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=model_metrics['Fall Risk Assessment']['r2_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "R² Score"},
                delta={'reference': 0.75},
                gauge={
                    'axis': {'range': [None, 1]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 0.6], 'color': "lightgray"},
                        {'range': [0.6, 0.8], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.85
                    }
                }
            ),
            row=1, col=2
        )
        
        # Anomaly detection model
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=model_metrics['Health Anomaly Detection']['accuracy'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Accuracy"},
                delta={'reference': 0.85},
                gauge={
                    'axis': {'range': [None, 1]},
                    'bar': {'color': "darkorange"},
                    'steps': [
                        {'range': [0, 0.75], 'color': "lightgray"},
                        {'range': [0.75, 0.9], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 0.95
                    }
                }
            ),
            row=1, col=3
        )
        
        fig.update_layout(
            height=400,
            title_text="🧠 ML Model Performance Dashboard",
            title_font_size=16
        )
        
        return fig
    
    def create_dashboard(self):
        """Create the complete bot analytics dashboard"""
        
        st.title("🤖 Singapore Senior Care Bot Analytics")
        st.markdown("### Performance monitoring and user engagement analytics")
        
        # Key metrics
        st.header("📊 Today's Key Metrics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        latest_data = self.bot_activity.iloc[-1]
        
        with col1:
            st.metric("Active Users", f"{int(latest_data['active_users'])}")
        
        with col2:
            adherence_rate = latest_data['medication_confirmations'] / latest_data['medication_reminders_sent']
            st.metric("Adherence Rate", f"{adherence_rate:.1%}")
        
        with col3:
            st.metric("Emergency Alerts", f"{int(latest_data['emergency_alerts'])}")
        
        with col4:
            st.metric("Satisfaction Score", f"{latest_data['user_satisfaction_score']:.1f}/5.0")
        
        with col5:
            st.metric("System Uptime", f"{latest_data['system_uptime_pct']:.1%}")
        
        # Main performance dashboard
        st.header("📈 Bot Performance Overview")
        performance_fig = self.create_bot_performance_overview()
        st.plotly_chart(performance_fig, use_container_width=True)
        
        # User demographics
        st.header("👥 User Demographics & Usage Patterns")
        demographics_fig = self.create_user_demographics_analysis()
        st.plotly_chart(demographics_fig, use_container_width=True)
        
        # ML model performance
        st.header("🧠 ML Model Performance")
        ml_fig = self.create_ml_model_performance()
        st.plotly_chart(ml_fig, use_container_width=True)

def main():
    """Main function to run the dashboards"""
    
    st.sidebar.title("🇸🇬 Singapore Senior Care")
    dashboard_choice = st.sidebar.selectbox(
        "Choose Dashboard",
        ["Health Overview", "Bot Analytics"]
    )
    
    if dashboard_choice == "Health Overview":
        health_dashboard = SingaporeHealthDashboard()
        health_dashboard.create_dashboard()
    else:
        bot_dashboard = SingaporeBotAnalyticsDashboard()
        bot_dashboard.create_dashboard()

if __name__ == "__main__":
    main()
