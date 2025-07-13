# Singapore Health Data Acquisition Script
# Download and prepare Singapore-specific datasets for the capstone project

import pandas as pd
import requests
import json
import os
from datetime import datetime, timedelta
import sqlite3

def setup_singapore_data_environment():
    """Set up the data environment for Singapore datasets"""
    
    # Create directories
    directories = [
        'data/singapore/moh_data',
        'data/singapore/singstat_data', 
        'data/singapore/processed',
        'data/singapore/raw',
        'models/singapore_models',
        'visualizations/singapore_dashboards'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def download_singapore_health_data():
    """
    Download Singapore health datasets from data.gov.sg
    Note: You'll need to register at data.gov.sg for API access
    """
    
    print("🇸🇬 Downloading Singapore Health Data...")
    
    # Singapore Open Data API endpoints
    datasets = {
        'hospital_bed_occupancy': 'https://data.gov.sg/api/action/datastore_search?resource_id=9ca5bbf8-2a36-468c-93ac-a2f0bdb9b4d9',
        'polyclinic_attendance': 'https://data.gov.sg/api/action/datastore_search?resource_id=67ce9692-2f34-4f4c-b5e1-7e6b5e7b3c8a',
        'chronic_disease_prevalence': 'https://data.gov.sg/api/action/datastore_search?resource_id=8c5b3c4e-9d2f-4a6b-8e3c-1f7a9b2d5e8f'
    }
    
    # Note: These are example endpoints - you'll need actual resource IDs from data.gov.sg
    
    for dataset_name, url in datasets.items():
        try:
            print(f"Downloading {dataset_name}...")
            # For demo purposes, we'll create simulated Singapore data
            # In real implementation, use: response = requests.get(url)
            
            singapore_data = create_simulated_singapore_data(dataset_name)
            
            # Save to CSV
            filename = f"data/singapore/raw/{dataset_name}.csv"
            singapore_data.to_csv(filename, index=False)
            print(f"✅ Saved {dataset_name} to {filename}")
            
        except Exception as e:
            print(f"❌ Error downloading {dataset_name}: {e}")
            # Create simulated data as fallback
            singapore_data = create_simulated_singapore_data(dataset_name)
            filename = f"data/singapore/raw/{dataset_name}_simulated.csv"
            singapore_data.to_csv(filename, index=False)
            print(f"✅ Created simulated {dataset_name} data")

def create_simulated_singapore_data(dataset_type):
    """Create realistic simulated Singapore health data"""
    
    import numpy as np
    np.random.seed(42)
    
    if dataset_type == 'hospital_bed_occupancy':
        # Singapore hospital bed occupancy data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        hospitals = ['SGH', 'NUH', 'TTSH', 'CGH', 'KTPH', 'AH', 'IMH', 'KKH']
        
        data = []
        for date in dates:
            for hospital in hospitals:
                # Simulate seasonal patterns and COVID impact
                base_occupancy = np.random.normal(0.75, 0.15)  # 75% average occupancy
                
                # Seasonal adjustments (monsoon season = more admissions)
                if date.month in [11, 12, 1, 2]:  # Northeast monsoon
                    base_occupancy += 0.1
                
                # Weekend patterns
                if date.weekday() >= 5:
                    base_occupancy -= 0.05
                    
                occupancy_rate = max(0.5, min(0.95, base_occupancy))
                
                data.append({
                    'date': date,
                    'hospital': hospital,
                    'total_beds': np.random.randint(500, 1500),
                    'occupied_beds': int(np.random.randint(500, 1500) * occupancy_rate),
                    'occupancy_rate': round(occupancy_rate, 3),
                    'elderly_patients_pct': round(np.random.normal(0.35, 0.1), 3)  # 35% elderly
                })
        
        return pd.DataFrame(data)
    
    elif dataset_type == 'polyclinic_attendance':
        # Singapore polyclinic attendance data
        dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
        polyclinics = ['Ang Mo Kio', 'Bedok', 'Bukit Batok', 'Clementi', 'Geylang', 
                      'Hougang', 'Jurong', 'Kallang', 'Marine Parade', 'Pasir Ris',
                      'Punggol', 'Queenstown', 'Sembawang', 'Sengkang', 'Tampines',
                      'Toa Payoh', 'Woodlands', 'Yishun']
        
        data = []
        for date in dates:
            for polyclinic in polyclinics:
                # Simulate attendance patterns
                base_attendance = np.random.normal(200, 50)  # Average daily attendance
                
                # Weekday vs weekend patterns
                if date.weekday() >= 5:
                    base_attendance *= 0.7  # Lower weekend attendance
                
                # Seasonal flu patterns
                if date.month in [6, 7, 8]:  # Mid-year flu season
                    base_attendance *= 1.2
                
                attendance = max(50, int(base_attendance))
                
                data.append({
                    'date': date,
                    'polyclinic': polyclinic,
                    'total_attendance': attendance,
                    'elderly_attendance': int(attendance * np.random.normal(0.4, 0.1)),  # 40% elderly
                    'chronic_disease_consultations': int(attendance * np.random.normal(0.25, 0.05)),
                    'medication_refills': int(attendance * np.random.normal(0.6, 0.1))
                })
        
        return pd.DataFrame(data)
    
    elif dataset_type == 'chronic_disease_prevalence':
        # Singapore chronic disease data by age group and district
        age_groups = ['60-64', '65-69', '70-74', '75-79', '80-84', '85+']
        districts = ['Central', 'East', 'North', 'North-East', 'West']
        conditions = ['Diabetes', 'Hypertension', 'Heart Disease', 'Stroke', 'Kidney Disease']
        
        data = []
        for district in districts:
            for age_group in age_groups:
                for condition in conditions:
                    # Simulate prevalence rates based on Singapore health studies
                    base_rates = {
                        'Diabetes': 0.25,      # 25% baseline
                        'Hypertension': 0.35,  # 35% baseline  
                        'Heart Disease': 0.15, # 15% baseline
                        'Stroke': 0.08,        # 8% baseline
                        'Kidney Disease': 0.12  # 12% baseline
                    }
                    
                    # Age adjustment - higher rates for older groups
                    age_multiplier = 1 + (age_groups.index(age_group) * 0.1)
                    prevalence = base_rates[condition] * age_multiplier
                    
                    # District variations (simulated socioeconomic factors)
                    district_adjustments = {
                        'Central': 1.0,
                        'East': 1.1,    # Slightly higher due to older population
                        'North': 0.95,
                        'North-East': 0.9,
                        'West': 1.05
                    }
                    
                    prevalence *= district_adjustments[district]
                    prevalence = min(0.8, prevalence)  # Cap at 80%
                    
                    data.append({
                        'district': district,
                        'age_group': age_group,
                        'condition': condition,
                        'prevalence_rate': round(prevalence, 3),
                        'estimated_cases': int(np.random.normal(1000, 200) * prevalence),
                        'year': 2024
                    })
        
        return pd.DataFrame(data)
    
    return pd.DataFrame()  # Empty dataframe for unknown types

def create_singapore_demographics_data():
    """Create Singapore demographics data relevant to senior care"""
    
    print("📊 Creating Singapore Demographics Data...")
    
    # HDB town data with senior population
    hdb_towns = [
        'Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Batok', 'Bukit Merah', 'Bukit Panjang',
        'Bukit Timah', 'Central Area', 'Choa Chu Kang', 'Clementi', 'Geylang', 'Hougang',
        'Jurong East', 'Jurong West', 'Kallang/Whampoa', 'Marine Parade', 'Pasir Ris',
        'Punggol', 'Queenstown', 'Sembawang', 'Sengkang', 'Serangoon', 'Tampines',
        'Toa Payoh', 'Woodlands', 'Yishun'
    ]
    
    demographic_data = []
    
    for town in hdb_towns:
        # Simulate realistic Singapore demographic data
        total_population = np.random.randint(80000, 300000)
        senior_population = int(total_population * np.random.normal(0.18, 0.05))  # ~18% seniors
        
        demographic_data.append({
            'town': town,
            'total_population': total_population,
            'senior_population_60plus': senior_population,
            'senior_percentage': round(senior_population / total_population, 3),
            'median_age': np.random.normal(42, 5),  # Singapore median age ~42
            'hdb_flats_total': int(total_population / 3.2),  # ~3.2 people per household
            'elderly_friendly_flats': int(total_population / 3.2 * np.random.normal(0.15, 0.05)),
            'healthcare_facilities': np.random.randint(1, 8),
            'avg_household_income': int(np.random.normal(9000, 2000)),  # SGD monthly
            'seniors_living_alone_pct': round(np.random.normal(0.12, 0.03), 3)  # 12% live alone
        })
    
    demographics_df = pd.DataFrame(demographic_data)
    demographics_df.to_csv('data/singapore/raw/singapore_demographics.csv', index=False)
    print("✅ Created Singapore demographics data")
    
    return demographics_df

def integrate_singapore_bot_data():
    """Integrate Singapore datasets with your bot data"""
    
    print("🔗 Integrating Singapore data with bot activity...")
    
    # Load your existing bot data
    if os.path.exists('data/bot_activity_data.csv'):
        bot_data = pd.read_csv('data/bot_activity_data.csv')
    else:
        print("❌ Bot activity data not found. Please run the main data generation first.")
        return
    
    # Load Singapore data
    demographics = pd.read_csv('data/singapore/raw/singapore_demographics.csv')
    
    # Add Singapore-specific context to bot users
    singapore_enhanced_data = []
    
    for _, user_row in bot_data.iterrows():
        # Assign users to Singapore towns
        town = np.random.choice(demographics['town'].values)
        town_data = demographics[demographics['town'] == town].iloc[0]
        
        # Add Singapore context
        enhanced_row = user_row.to_dict()
        enhanced_row.update({
            'singapore_town': town,
            'hdb_flat_type': np.random.choice(['1-room', '2-room', '3-room', '4-room', '5-room'], 
                                            p=[0.05, 0.15, 0.25, 0.35, 0.2]),
            'pioneer_generation': np.random.choice([0, 1], p=[0.7, 0.3]),  # 30% pioneer generation
            'medisave_balance': np.random.normal(25000, 10000),  # SGD
            'has_family_nearby': np.random.choice([0, 1], p=[0.3, 0.7]),  # 70% have family nearby
            'preferred_language': np.random.choice(['English', 'Mandarin', 'Malay', 'Tamil'], 
                                                 p=[0.5, 0.3, 0.15, 0.05]),
            'healthcare_subsidy_eligible': np.random.choice([0, 1], p=[0.4, 0.6])
        })
        
        singapore_enhanced_data.append(enhanced_row)
    
    singapore_bot_df = pd.DataFrame(singapore_enhanced_data)
    singapore_bot_df.to_csv('data/singapore/processed/singapore_enhanced_bot_data.csv', index=False)
    print("✅ Created Singapore-enhanced bot data")
    
    return singapore_bot_df

def main():
    """Main function to set up Singapore data environment"""
    
    print("🇸🇬 Setting up Singapore Senior Care Data Environment...")
    print("=" * 60)
    
    # Step 1: Create directory structure
    setup_singapore_data_environment()
    
    # Step 2: Download/simulate Singapore health data
    download_singapore_health_data()
    
    # Step 3: Create demographics data
    create_singapore_demographics_data()
    
    # Step 4: Integrate with bot data
    integrate_singapore_bot_data()
    
    print("\n🎉 Singapore data environment setup complete!")
    print("\n📊 Available datasets:")
    print("- MOH Hospital bed occupancy data")
    print("- Polyclinic attendance patterns")  
    print("- Chronic disease prevalence by district")
    print("- Singapore demographics and HDB data")
    print("- Singapore-enhanced bot activity data")
    
    print("\n🚀 Next steps:")
    print("1. Review the generated datasets in data/singapore/")
    print("2. Register at data.gov.sg for real dataset access")
    print("3. Run the ML model training scripts")
    print("4. Create Singapore-specific visualizations")

if __name__ == "__main__":
    import numpy as np
    main()
