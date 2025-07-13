# Basic Singapore Data Setup (No ML Dependencies)
# This version works without pandas/numpy for initial testing

import json
import os
import random
from datetime import datetime, timedelta

def setup_singapore_data_basic():
    """Set up basic Singapore data structure without heavy dependencies"""
    
    print("🇸🇬 Setting up Singapore Senior Care Data (Basic Version)...")
    
    # Create directories
    directories = [
        'data/singapore/basic',
        'data/singapore/processed', 
        'models/singapore_models'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}/")
    
    # Create basic Singapore health data
    singapore_towns = [
        'Ang Mo Kio', 'Bedok', 'Bishan', 'Bukit Batok', 'Bukit Merah',
        'Clementi', 'Hougang', 'Jurong East', 'Tampines', 'Toa Payoh',
        'Woodlands', 'Yishun', 'Sengkang', 'Punggol', 'Serangoon'
    ]
    
    # Generate basic demographics data
    demographics_data = []
    for town in singapore_towns:
        town_data = {
            'town': town,
            'total_population': random.randint(80000, 300000),
            'senior_population_60plus': random.randint(15000, 55000),
            'healthcare_facilities': random.randint(2, 8),
            'polyclinics': random.randint(1, 3),
            'elderly_friendly_housing_pct': round(random.uniform(0.10, 0.25), 2),
            'avg_household_income_sgd': random.randint(7000, 12000)
        }
        demographics_data.append(town_data)
    
    # Save demographics data
    with open('data/singapore/basic/demographics.json', 'w') as f:
        json.dump(demographics_data, f, indent=2)
    print("✅ Created Singapore demographics data")
    
    # Generate basic health conditions data
    health_conditions = ['Diabetes', 'Hypertension', 'Heart Disease', 'Stroke', 'Kidney Disease']
    districts = ['Central', 'East', 'North', 'North-East', 'West']
    
    health_data = []
    for district in districts:
        for condition in health_conditions:
            condition_data = {
                'district': district,
                'condition': condition,
                'prevalence_rate': round(random.uniform(0.15, 0.35), 3),
                'estimated_cases': random.randint(5000, 25000),
                'year': 2024
            }
            health_data.append(condition_data)
    
    with open('data/singapore/basic/health_conditions.json', 'w') as f:
        json.dump(health_data, f, indent=2)
    print("✅ Created Singapore health conditions data")
    
    # Generate sample bot user data for Singapore
    bot_users = []
    for i in range(100):  # 100 sample senior users
        user_data = {
            'user_id': f'sg_senior_{i+1}',
            'age': random.randint(60, 90),
            'town': random.choice(singapore_towns),
            'hdb_flat_type': random.choice(['2-room', '3-room', '4-room', '5-room']),
            'has_family_nearby': random.choice([True, False]),
            'pioneer_generation': random.choice([True, False]),
            'chronic_conditions': random.randint(1, 4),
            'medications_per_day': random.randint(2, 8),
            'technology_comfort_level': random.randint(1, 5),
            'preferred_language': random.choice(['English', 'Mandarin', 'Malay', 'Tamil'])
        }
        bot_users.append(user_data)
    
    with open('data/singapore/basic/bot_users.json', 'w') as f:
        json.dump(bot_users, f, indent=2)
    print("✅ Created Singapore bot users data")
    
    # Create a basic ML models simulation (no actual ML)
    models_status = {
        'medication_adherence_model': {
            'status': 'simulated',
            'accuracy': 0.87,
            'features': ['age', 'chronic_conditions', 'family_support', 'hdb_type'],
            'last_trained': datetime.now().isoformat()
        },
        'fall_risk_model': {
            'status': 'simulated', 
            'r2_score': 0.82,
            'features': ['age', 'medications', 'mobility', 'home_hazards'],
            'last_trained': datetime.now().isoformat()
        },
        'health_anomaly_model': {
            'status': 'simulated',
            'accuracy': 0.91,
            'features': ['daily_activity', 'vital_signs', 'medication_compliance'],
            'last_trained': datetime.now().isoformat()
        }
    }
    
    with open('models/singapore_models/models_status.json', 'w') as f:
        json.dump(models_status, f, indent=2)
    print("✅ Created ML models status (simulated)")
    
    return True

def create_basic_visualization_data():
    """Create data for basic visualizations without plotly/streamlit"""
    
    print("\n📊 Creating visualization data...")
    
    # Daily medication adherence data (last 30 days)
    adherence_data = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        adherence_data.append({
            'date': date,
            'adherence_rate': round(random.uniform(0.75, 0.95), 3),
            'total_reminders': random.randint(200, 400),
            'successful_takes': random.randint(150, 380)
        })
    
    with open('data/singapore/basic/adherence_trends.json', 'w') as f:
        json.dump(adherence_data, f, indent=2)
    
    # Emergency alerts data
    emergency_data = []
    for i in range(7):  # Last 7 days
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        emergency_data.append({
            'date': date,
            'fall_alerts': random.randint(0, 3),
            'medication_missed_alerts': random.randint(5, 20),
            'emergency_locations': random.randint(0, 2)
        })
    
    with open('data/singapore/basic/emergency_trends.json', 'w') as f:
        json.dump(emergency_data, f, indent=2)
    
    print("✅ Created basic visualization data")
    
    return True

def generate_singapore_report():
    """Generate a text-based report of the Singapore data"""
    
    print("\n📋 SINGAPORE SENIOR CARE DATA REPORT")
    print("=" * 50)
    
    # Load and summarize demographics
    try:
        with open('data/singapore/basic/demographics.json', 'r') as f:
            demographics = json.load(f)
        
        total_population = sum(town['total_population'] for town in demographics)
        total_seniors = sum(town['senior_population_60plus'] for town in demographics)
        senior_percentage = (total_seniors / total_population) * 100
        
        print(f"\n🇸🇬 SINGAPORE DEMOGRAPHICS:")
        print(f"   Total Population: {total_population:,}")
        print(f"   Senior Population (60+): {total_seniors:,}")
        print(f"   Senior Percentage: {senior_percentage:.1f}%")
        print(f"   Towns Covered: {len(demographics)}")
        
    except FileNotFoundError:
        print("   ❌ Demographics data not found")
    
    # Load and summarize health conditions
    try:
        with open('data/singapore/basic/health_conditions.json', 'r') as f:
            health_data = json.load(f)
        
        conditions = set(item['condition'] for item in health_data)
        districts = set(item['district'] for item in health_data)
        
        print(f"\n🏥 HEALTH CONDITIONS DATA:")
        print(f"   Conditions Tracked: {len(conditions)}")
        print(f"   Districts: {len(districts)}")
        print(f"   Data Points: {len(health_data)}")
        
        # Show top conditions by prevalence
        condition_rates = {}
        for item in health_data:
            condition = item['condition']
            if condition not in condition_rates:
                condition_rates[condition] = []
            condition_rates[condition].append(item['prevalence_rate'])
        
        print(f"\n   Top Health Conditions:")
        for condition, rates in condition_rates.items():
            avg_rate = sum(rates) / len(rates)
            print(f"   • {condition}: {avg_rate:.1%} average prevalence")
            
    except FileNotFoundError:
        print("   ❌ Health conditions data not found")
    
    # Load and summarize bot users
    try:
        with open('data/singapore/basic/bot_users.json', 'r') as f:
            users = json.load(f)
        
        avg_age = sum(user['age'] for user in users) / len(users)
        family_support = sum(1 for user in users if user['has_family_nearby']) / len(users)
        pioneer_gen = sum(1 for user in users if user['pioneer_generation']) / len(users)
        
        print(f"\n🤖 BOT USERS DATA:")
        print(f"   Total Users: {len(users)}")
        print(f"   Average Age: {avg_age:.1f} years")
        print(f"   Has Family Nearby: {family_support:.1%}")
        print(f"   Pioneer Generation: {pioneer_gen:.1%}")
        
        # Language distribution
        languages = {}
        for user in users:
            lang = user['preferred_language']
            languages[lang] = languages.get(lang, 0) + 1
        
        print(f"\n   Language Preferences:")
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(users)) * 100
            print(f"   • {lang}: {count} users ({percentage:.1f}%)")
            
    except FileNotFoundError:
        print("   ❌ Bot users data not found")
    
    # ML Models status
    try:
        with open('models/singapore_models/models_status.json', 'r') as f:
            models = json.load(f)
        
        print(f"\n🧠 MACHINE LEARNING MODELS:")
        for model_name, model_info in models.items():
            print(f"   • {model_name.replace('_', ' ').title()}")
            print(f"     Status: {model_info['status']}")
            if 'accuracy' in model_info:
                print(f"     Accuracy: {model_info['accuracy']:.1%}")
            if 'r2_score' in model_info:
                print(f"     R² Score: {model_info['r2_score']:.3f}")
            print(f"     Features: {len(model_info['features'])}")
            
    except FileNotFoundError:
        print("   ❌ Models status not found")
    
    print(f"\n🎉 Singapore Senior Care Data Setup Complete!")
    print(f"📁 Data files saved in: data/singapore/basic/")
    print(f"🤖 Models info saved in: models/singapore_models/")
    
    return True

def main():
    """Main function to set up basic Singapore data"""
    
    print("🇸🇬 SINGAPORE SENIOR CARE - BASIC SETUP")
    print("(No heavy ML dependencies required)")
    print("=" * 60)
    
    # Step 1: Set up basic data
    setup_singapore_data_basic()
    
    # Step 2: Create visualization data
    create_basic_visualization_data()
    
    # Step 3: Generate report
    generate_singapore_report()
    
    print(f"\n✅ SETUP COMPLETE!")
    print(f"\n🚀 Next Steps:")
    print(f"   1. Your bot is ready: python bot.py")
    print(f"   2. View data files: data/singapore/basic/")
    print(f"   3. Install ML packages later: pip install pandas numpy scikit-learn")
    print(f"   4. Run full ML setup: python singapore_ml_models.py")
    
    return True

if __name__ == "__main__":
    main()
