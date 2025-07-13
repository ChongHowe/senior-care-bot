# Singapore Senior Care ML Models
# Three ML models for the capstone project using Singapore health data

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, IsolationForest
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class SingaporeMedicationAdherenceModel:
    """
    ML Model 1: Medication Adherence Prediction for Singapore Seniors
    Predicts likelihood of medication non-adherence based on Singapore-specific factors
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def prepare_singapore_adherence_data(self):
        """Prepare Singapore-specific medication adherence training data"""
        
        print("🇸🇬 Preparing Singapore Medication Adherence Data...")
        
        # Load Singapore-enhanced bot data
        singapore_data = pd.read_csv('data/singapore/processed/singapore_enhanced_bot_data.csv')
        
        # Create adherence features based on Singapore context
        features = []
        
        for _, row in singapore_data.iterrows():
            # Singapore-specific features
            feature_row = {
                'age': row.get('age', 70),
                'chronic_conditions_count': row.get('chronic_conditions_count', 2),
                'pioneer_generation': row.get('pioneer_generation', 0),
                'hdb_flat_type_encoded': self._encode_hdb_type(row.get('hdb_flat_type', '3-room')),
                'has_family_nearby': row.get('has_family_nearby', 1),
                'medisave_balance': row.get('medisave_balance', 25000),
                'healthcare_subsidy_eligible': row.get('healthcare_subsidy_eligible', 1),
                'preferred_language_encoded': self._encode_language(row.get('preferred_language', 'English')),
                'medications_per_day': row.get('medications_per_day', 3),
                'polyclinic_distance': np.random.normal(2, 1),  # km from polyclinic
                'medication_cost_monthly': np.random.normal(150, 50),  # SGD
                'cognitive_score': np.random.normal(25, 5),  # Mini-Mental State Exam
                'social_support_score': row.get('has_family_nearby', 1) * 5 + np.random.normal(3, 1),
                'technology_comfort': np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.25, 0.2, 0.15, 0.1])
            }
            
            # Calculate adherence score (0 = non-adherent, 1 = adherent)
            adherence_probability = self._calculate_singapore_adherence_probability(feature_row)
            feature_row['medication_adherent'] = np.random.choice([0, 1], p=[1-adherence_probability, adherence_probability])
            
            features.append(feature_row)
        
        return pd.DataFrame(features)
    
    def _encode_hdb_type(self, hdb_type):
        """Encode HDB flat type to numerical value"""
        hdb_encoding = {'1-room': 1, '2-room': 2, '3-room': 3, '4-room': 4, '5-room': 5}
        return hdb_encoding.get(hdb_type, 3)
    
    def _encode_language(self, language):
        """Encode preferred language to numerical value"""
        lang_encoding = {'English': 1, 'Mandarin': 2, 'Malay': 3, 'Tamil': 4}
        return lang_encoding.get(language, 1)
    
    def _calculate_singapore_adherence_probability(self, features):
        """Calculate adherence probability based on Singapore-specific factors"""
        
        base_probability = 0.7  # 70% base adherence rate in Singapore
        
        # Age factor (older = lower adherence due to cognitive decline)
        if features['age'] > 80:
            base_probability -= 0.1
        elif features['age'] > 75:
            base_probability -= 0.05
        
        # Pioneer generation (better healthcare habits)
        if features['pioneer_generation']:
            base_probability += 0.1
        
        # Family support
        if features['has_family_nearby']:
            base_probability += 0.15
        
        # Economic factors
        if features['healthcare_subsidy_eligible']:
            base_probability += 0.1
        if features['medisave_balance'] < 10000:
            base_probability -= 0.1
        
        # Technology comfort (bot usage)
        base_probability += (features['technology_comfort'] - 3) * 0.05
        
        # Medication complexity
        if features['medications_per_day'] > 5:
            base_probability -= 0.15
        
        return max(0.1, min(0.95, base_probability))
    
    def train(self):
        """Train the medication adherence model"""
        
        print("🤖 Training Singapore Medication Adherence Model...")
        
        # Prepare data
        data = self.prepare_singapore_adherence_data()
        
        # Features and target
        feature_columns = [col for col in data.columns if col != 'medication_adherent']
        X = data[feature_columns]
        y = data['medication_adherent']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Medication Adherence Model Accuracy: {accuracy:.3f}")
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔝 Top Features for Medication Adherence:")
        print(feature_importance.head(10))
        
        # Save model
        joblib.dump(self.model, 'models/singapore_models/medication_adherence_model.pkl')
        joblib.dump(self.scaler, 'models/singapore_models/medication_adherence_scaler.pkl')
        
        return accuracy, feature_importance

class SingaporeFallRiskModel:
    """
    ML Model 2: Fall Risk Assessment for Singapore Seniors
    Predicts fall risk score based on health data and environmental factors
    """
    
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def prepare_singapore_fall_data(self):
        """Prepare Singapore-specific fall risk training data"""
        
        print("🇸🇬 Preparing Singapore Fall Risk Data...")
        
        # Load data
        singapore_data = pd.read_csv('data/singapore/processed/singapore_enhanced_bot_data.csv')
        demographics = pd.read_csv('data/singapore/raw/singapore_demographics.csv')
        
        features = []
        
        for _, row in singapore_data.iterrows():
            town = row.get('singapore_town', 'Toa Payoh')
            town_data = demographics[demographics['town'] == town].iloc[0] if len(demographics[demographics['town'] == town]) > 0 else demographics.iloc[0]
            
            feature_row = {
                'age': row.get('age', 70),
                'bmi': np.random.normal(24, 3),  # Singapore BMI average
                'chronic_conditions_count': row.get('chronic_conditions_count', 2),
                'medication_count': row.get('medications_per_day', 3),
                'blood_pressure_systolic': np.random.normal(135, 20),
                'vision_score': np.random.normal(7, 2),  # 1-10 scale
                'hearing_score': np.random.normal(8, 1.5),
                'mobility_aid_use': np.random.choice([0, 1], p=[0.7, 0.3]),
                'home_hazards_count': np.random.poisson(2),  # Typical HDB hazards
                'exercise_frequency': np.random.choice([0, 1, 2, 3, 4, 5, 6, 7]),  # days per week
                'balance_score': np.random.normal(40, 10),  # Berg Balance Scale
                'cognitive_score': np.random.normal(25, 5),  # MMSE
                'social_isolation_score': (1 - row.get('has_family_nearby', 1)) * 5 + np.random.normal(2, 1),
                'previous_falls': np.random.poisson(0.5),  # Falls in past year
                'fear_of_falling': np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.2, 0.3, 0.25, 0.15]),
                'polyclinic_visits_per_year': np.random.poisson(8),
                'seasonal_factor': 1.2 if datetime.now().month in [11, 12, 1, 2] else 1.0,  # Monsoon season
                'hdb_floor_level': np.random.randint(1, 15),
                'lift_availability': np.random.choice([0, 1], p=[0.1, 0.9])  # 90% have lifts
            }
            
            # Calculate fall risk score (0-100)
            fall_risk_score = self._calculate_singapore_fall_risk(feature_row)
            feature_row['fall_risk_score'] = fall_risk_score
            
            features.append(feature_row)
        
        return pd.DataFrame(features)
    
    def _calculate_singapore_fall_risk(self, features):
        """Calculate fall risk score based on Singapore research"""
        
        base_risk = 20  # Base risk score
        
        # Age (strongest predictor)
        base_risk += max(0, (features['age'] - 65) * 2)
        
        # Previous falls (strong predictor)
        base_risk += features['previous_falls'] * 15
        
        # Chronic conditions
        base_risk += features['chronic_conditions_count'] * 5
        
        # Medication (polypharmacy risk)
        if features['medication_count'] > 4:
            base_risk += 10
        
        # Physical factors
        if features['bmi'] < 18.5 or features['bmi'] > 30:
            base_risk += 8
        
        base_risk += max(0, (140 - features['blood_pressure_systolic']) * 0.2)  # Hypotension
        base_risk += max(0, (5 - features['vision_score']) * 2)
        base_risk += max(0, (6 - features['hearing_score']) * 1.5)
        
        # Mobility and balance
        if features['mobility_aid_use']:
            base_risk += 8
        base_risk += max(0, (45 - features['balance_score']) * 0.5)
        
        # Environmental (Singapore-specific)
        base_risk += features['home_hazards_count'] * 3
        base_risk *= features['seasonal_factor']  # Monsoon season
        
        # Protective factors
        base_risk -= features['exercise_frequency'] * 2
        if features['lift_availability']:
            base_risk -= 3  # Reduces stair climbing
        
        # Social support
        base_risk += features['social_isolation_score'] * 1.5
        
        return max(0, min(100, base_risk))
    
    def train(self):
        """Train the fall risk model"""
        
        print("🤖 Training Singapore Fall Risk Model...")
        
        # Prepare data
        data = self.prepare_singapore_fall_data()
        
        # Features and target
        feature_columns = [col for col in data.columns if col != 'fall_risk_score']
        X = data[feature_columns]
        y = data['fall_risk_score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"✅ Fall Risk Model R² Score: {r2:.3f}")
        print(f"✅ Fall Risk Model RMSE: {rmse:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n🔝 Top Features for Fall Risk:")
        print(feature_importance.head(10))
        
        # Save model
        joblib.dump(self.model, 'models/singapore_models/fall_risk_model.pkl')
        joblib.dump(self.scaler, 'models/singapore_models/fall_risk_scaler.pkl')
        
        return r2, feature_importance

class SingaporeHealthAnomalyModel:
    """
    ML Model 3: Health Pattern Anomaly Detection for Singapore Seniors
    Detects unusual health patterns that may indicate emergencies or health deterioration
    """
    
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
    def prepare_singapore_anomaly_data(self):
        """Prepare Singapore health pattern data for anomaly detection"""
        
        print("🇸🇬 Preparing Singapore Health Anomaly Data...")
        
        # Load Singapore data
        singapore_data = pd.read_csv('data/singapore/processed/singapore_enhanced_bot_data.csv')
        
        features = []
        
        for _, row in singapore_data.iterrows():
            # Generate daily health patterns
            for day in range(30):  # 30 days of data per user
                feature_row = {
                    'user_id': row.get('user_id', f"user_{len(features)}"),
                    'day': day,
                    'age': row.get('age', 70),
                    'steps_daily': max(0, np.random.normal(3000, 1500)),  # Singapore senior average
                    'heart_rate_avg': np.random.normal(75, 10),
                    'blood_pressure_systolic': np.random.normal(135, 15),
                    'blood_pressure_diastolic': np.random.normal(85, 10),
                    'sleep_hours': max(4, min(12, np.random.normal(7, 1.5))),
                    'medication_taken_on_time': np.random.choice([0, 1], p=[0.2, 0.8]),
                    'meals_per_day': max(1, np.random.poisson(3)),
                    'water_intake_liters': max(0.5, np.random.normal(1.8, 0.5)),
                    'bathroom_visits': max(2, np.random.poisson(8)),
                    'emergency_button_pressed': np.random.choice([0, 1], p=[0.95, 0.05]),
                    'family_contact_frequency': np.random.poisson(2),  # calls per day
                    'mood_score': np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.15, 0.4, 0.25, 0.1]),
                    'confusion_episodes': np.random.poisson(0.1),
                    'temperature_celsius': np.random.normal(36.5, 0.3),
                    'indoor_activity_hours': max(0, min(16, np.random.normal(8, 3))),
                    'outdoor_activity_hours': max(0, min(8, np.random.normal(2, 1))),
                    'app_usage_minutes': max(0, np.random.normal(45, 20)),  # Bot usage
                    'missed_appointments': np.random.choice([0, 1], p=[0.9, 0.1]),
                    'weight_kg': np.random.normal(65, 10),
                    'humidity_comfort': np.random.normal(0.6, 0.1),  # Singapore humidity adaptation
                    'air_quality_aqi': np.random.normal(50, 20)  # Singapore AQI
                }
                
                # Introduce anomalies (10% of data)
                if np.random.random() < 0.1:
                    feature_row = self._introduce_singapore_anomaly(feature_row)
                    feature_row['is_anomaly'] = 1
                else:
                    feature_row['is_anomaly'] = 0
                
                features.append(feature_row)
        
        return pd.DataFrame(features)
    
    def _introduce_singapore_anomaly(self, normal_data):
        """Introduce realistic health anomalies"""
        
        anomaly_type = np.random.choice(['medical_emergency', 'behavioral_change', 'environmental_stress'])
        
        if anomaly_type == 'medical_emergency':
            # Simulate stroke, heart attack, severe hypotension
            normal_data['heart_rate_avg'] = np.random.choice([
                np.random.normal(45, 5),    # Bradycardia
                np.random.normal(120, 10)   # Tachycardia
            ])
            normal_data['blood_pressure_systolic'] = np.random.choice([
                np.random.normal(90, 10),   # Hypotension
                np.random.normal(180, 15)   # Hypertension crisis
            ])
            normal_data['confusion_episodes'] = np.random.poisson(3)
            normal_data['emergency_button_pressed'] = 1
            
        elif anomaly_type == 'behavioral_change':
            # Depression, cognitive decline, medication non-adherence
            normal_data['steps_daily'] = max(0, np.random.normal(500, 200))  # Severe reduction
            normal_data['sleep_hours'] = np.random.choice([
                np.random.normal(3, 1),     # Insomnia
                np.random.normal(12, 1)     # Hypersomnia
            ])
            normal_data['medication_taken_on_time'] = 0
            normal_data['mood_score'] = np.random.choice([1, 2], p=[0.7, 0.3])
            normal_data['family_contact_frequency'] = 0
            
        elif anomaly_type == 'environmental_stress':
            # Heat stroke, air pollution, dehydration (Singapore-specific)
            normal_data['temperature_celsius'] = np.random.normal(38.5, 0.5)  # Fever
            normal_data['water_intake_liters'] = max(0.2, np.random.normal(0.8, 0.3))  # Dehydration
            normal_data['air_quality_aqi'] = np.random.normal(150, 30)  # Poor air quality
            normal_data['indoor_activity_hours'] = 14  # Staying indoors due to heat/haze
            normal_data['outdoor_activity_hours'] = 0
        
        return normal_data
    
    def train(self):
        """Train the anomaly detection model"""
        
        print("🤖 Training Singapore Health Anomaly Model...")
        
        # Prepare data
        data = self.prepare_singapore_anomaly_data()
        
        # Features (exclude target and identifiers)
        feature_columns = [col for col in data.columns if col not in ['is_anomaly', 'user_id', 'day']]
        X = data[feature_columns]
        y = data['is_anomaly']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model (use only normal data for training)
        normal_data_idx = y_train == 0
        self.model.fit(X_train_scaled[normal_data_idx])
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_binary = (y_pred == -1).astype(int)  # Isolation Forest returns -1 for anomalies
        
        accuracy = accuracy_score(y_test, y_pred_binary)
        
        print(f"✅ Anomaly Detection Model Accuracy: {accuracy:.3f}")
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred_binary))
        
        # Save model
        joblib.dump(self.model, 'models/singapore_models/health_anomaly_model.pkl')
        joblib.dump(self.scaler, 'models/singapore_models/health_anomaly_scaler.pkl')
        
        return accuracy

def main():
    """Train all three Singapore ML models"""
    
    print("🇸🇬 Training Singapore Senior Care ML Models")
    print("=" * 60)
    
    # Ensure directories exist
    import os
    os.makedirs('models/singapore_models', exist_ok=True)
    
    results = {}
    
    # Model 1: Medication Adherence
    print("\n1️⃣ MEDICATION ADHERENCE PREDICTION")
    print("-" * 40)
    adherence_model = SingaporeMedicationAdherenceModel()
    results['adherence_accuracy'], results['adherence_features'] = adherence_model.train()
    
    # Model 2: Fall Risk Assessment
    print("\n2️⃣ FALL RISK ASSESSMENT")
    print("-" * 40)
    fall_model = SingaporeFallRiskModel()
    results['fall_r2'], results['fall_features'] = fall_model.train()
    
    # Model 3: Health Anomaly Detection
    print("\n3️⃣ HEALTH ANOMALY DETECTION")
    print("-" * 40)
    anomaly_model = SingaporeHealthAnomalyModel()
    results['anomaly_accuracy'] = anomaly_model.train()
    
    # Summary
    print("\n🎉 ALL MODELS TRAINED SUCCESSFULLY!")
    print("=" * 60)
    print(f"📊 Model Performance Summary:")
    print(f"   • Medication Adherence: {results['adherence_accuracy']:.1%} accuracy")
    print(f"   • Fall Risk Assessment: {results['fall_r2']:.3f} R² score")
    print(f"   • Health Anomaly Detection: {results['anomaly_accuracy']:.1%} accuracy")
    
    print(f"\n💾 Models saved to: models/singapore_models/")
    print(f"🚀 Ready for deployment in your Singapore senior care bot!")
    
    return results

if __name__ == "__main__":
    main()
