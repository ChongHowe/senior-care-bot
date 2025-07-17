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
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# --- Security Utilities ---
from security_utils import sanitize_input, encrypt_data, decrypt_data, generate_fernet_key

# Load or generate encryption key (for demonstration, use a static key; in production, load from .env)
FERNET_KEY = generate_fernet_key()


# --- Multi-country Medication Adherence Model ---
class MedicationAdherenceModel:
    """
    ML Model 1: Medication Adherence Prediction for Seniors (Multi-country)
    Predicts likelihood of medication non-adherence based on country-specific factors
    """
    
    COUNTRY_PARAMS = {
        'Singapore': {
            'adherence_rate': 0.7,
            'feature_mod': lambda f: f,  # No change
        },
        'US': {
            'adherence_rate': 0.55,
            'feature_mod': lambda f: {**f, 'medication_cost_monthly': np.random.normal(350, 100), 'has_family_nearby': np.random.choice([0,1],p=[0.5,0.5])},
        },
        'Japan': {
            'adherence_rate': 0.8,
            'feature_mod': lambda f: {**f, 'technology_comfort': np.random.choice([3,4,5],p=[0.2,0.4,0.4]), 'preferred_language_encoded': 1},
        },
        'UK': {
            'adherence_rate': 0.7,
            'feature_mod': lambda f: {**f, 'medication_cost_monthly': np.random.normal(50, 20), 'healthcare_subsidy_eligible': 1},
        },
    }

    def __init__(self, country='Singapore'):
        self.country = country
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
        self.scaler = StandardScaler()
        self.label_encoders = {}

    def _encode_hdb_type(self, hdb_type):
        hdb_encoding = {'1-room': 1, '2-room': 2, '3-room': 3, '4-room': 4, '5-room': 5}
        return hdb_encoding.get(hdb_type, 3)

    def _encode_language(self, language):
        lang_encoding = {'English': 1, 'Mandarin': 2, 'Malay': 3, 'Tamil': 4}
        return lang_encoding.get(language, 1)

    def _calculate_adherence_probability(self, features):
        # Use country-specific base adherence rate
        base_probability = self.COUNTRY_PARAMS[self.country]['adherence_rate']
        # Age factor (older = lower adherence due to cognitive decline)
        if features['age'] > 80:
            base_probability -= 0.1
        elif features['age'] > 75:
            base_probability -= 0.05
        # Family support
        if features.get('has_family_nearby', 1):
            base_probability += 0.12
        # Economic factors
        if features.get('healthcare_subsidy_eligible', 1):
            base_probability += 0.08
        if features.get('medisave_balance', 25000) < 10000:
            base_probability -= 0.08
        # Technology comfort (bot usage)
        base_probability += (features.get('technology_comfort', 3) - 3) * 0.04
        # Medication complexity
        if features.get('medications_per_day', 3) > 5:
            base_probability -= 0.12
        return max(0.1, min(0.95, base_probability))

    def prepare_adherence_data(self, n_samples=500):
        print(f"🌏 Preparing Medication Adherence Data for {self.country}...")
        # Load Singapore-enhanced bot data as base
        base_data = pd.read_csv('data/singapore/processed/singapore_enhanced_bot_data.csv')
        features = []
        data_rows = list(base_data.iterrows())
        for i in range(n_samples):
            _, row = data_rows[i % len(data_rows)]
            # Sanitize all string inputs from external data
            hdb_flat_type = sanitize_input(str(row.get('hdb_flat_type', '3-room')))
            preferred_language = sanitize_input(str(row.get('preferred_language', 'English')))
            feature_row = {
                'age': row.get('age', 70),
                'chronic_conditions_count': row.get('chronic_conditions_count', 2),
                'pioneer_generation': row.get('pioneer_generation', 0),
                'hdb_flat_type_encoded': self._encode_hdb_type(hdb_flat_type),
                'has_family_nearby': row.get('has_family_nearby', 1),
                'medisave_balance': row.get('medisave_balance', 25000),
                'healthcare_subsidy_eligible': row.get('healthcare_subsidy_eligible', 1),
                'preferred_language_encoded': self._encode_language(preferred_language),
                'medications_per_day': row.get('medications_per_day', 3),
                'polyclinic_distance': np.random.normal(2, 1),
                'medication_cost_monthly': np.random.normal(150, 50),
                'cognitive_score': np.random.normal(25, 5),
                'social_support_score': row.get('has_family_nearby', 1) * 5 + np.random.normal(3, 1),
                'technology_comfort': np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.25, 0.2, 0.15, 0.1])
            }
            # Apply country-specific feature modifications
            feature_row = self.COUNTRY_PARAMS[self.country]['feature_mod'](feature_row)
            adherence_probability = self._calculate_adherence_probability(feature_row)
            feature_row['medication_adherent'] = np.random.choice([0, 1], p=[1-adherence_probability, adherence_probability])
            features.append(feature_row)
        return pd.DataFrame(features)

    def train(self, n_samples=500, output_prefix='singapore_models'):
        print(f"🤖 Training Medication Adherence Model for {self.country}...")
        data = self.prepare_adherence_data(n_samples=n_samples)
        feature_columns = [col for col in data.columns if col != 'medication_adherent']
        X = data[feature_columns]
        y = data['medication_adherent']
        print("Class distribution (all data):")
        print(y.value_counts())
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)
        print("Class distribution (train):")
        print(y_train.value_counts())
        print("Class distribution (test):")
        print(y_test.value_counts())
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        self.model.fit(X_train_scaled, y_train)
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        # Interactive Feature Importance Plot
        fig1 = px.bar(feature_importance.head(10), x='importance', y='feature', orientation='h',
                     title=f'Top 10 Features for Medication Adherence ({self.country})', color='importance', color_continuous_scale='Viridis')
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        fig1.write_html(f'models/{output_prefix}/adherence_feature_importance_{self.country}.html')
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred)
        fig2 = px.imshow(
            cm,
            text_auto=True,
            color_continuous_scale='Viridis',
            labels=dict(x="Predicted", y="Actual", color="Count"),
            title=f"Confusion Matrix - Medication Adherence ({self.country})"
        )
        fig2.update_traces(
            textfont=dict(color="black", size=32, family="Arial Black, Arial, sans-serif")
        )
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                fig2.add_annotation(
                    x=j,
                    y=i,
                    text=str(cm[i, j]),
                    showarrow=False,
                    font=dict(color="black", size=32, family="Arial Black, Arial, sans-serif"),
                    bgcolor="white",
                    opacity=0.9
                )
        fig2.update_layout(
            xaxis_title="Predicted",
            yaxis_title="Actual",
            font=dict(color="black", size=18),
            coloraxis_colorbar=dict(title="Count")
        )
        fig2.write_html(f'models/{output_prefix}/adherence_confusion_matrix_{self.country}.html')
        print(f"✅ {self.country} Medication Adherence Model Accuracy: {accuracy:.3f}")
        print("\n📊 Classification Report:")
        print(classification_report(y_test, y_pred))
        print("\n🔝 Top Features for Medication Adherence:")
        print(feature_importance.head(10))
        # Save model
        # Save model (optionally encrypt model file)
        model_path = f'models/{output_prefix}/medication_adherence_model_{self.country}.pkl'
        scaler_path = f'models/{output_prefix}/medication_adherence_scaler_{self.country}.pkl'
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        # Example: Encrypt model file (optional, for demonstration)
        # with open(model_path, 'rb') as f:
        #     encrypted = encrypt_data(f.read(), FERNET_KEY)
        # with open(model_path + '.enc', 'wb') as f:
        #     f.write(encrypted)
        return accuracy, feature_importance, cm

# --- Multi-country comparison function ---
def compare_countries_adherence():
    countries = ['Singapore', 'US', 'Japan', 'UK']
    results = {}
    for country in countries:
        print(f"\n=== {country} ===")
        model = MedicationAdherenceModel(country=country)
        accuracy, feature_importance, cm = model.train(n_samples=500, output_prefix='singapore_models')
        results[country] = {
            'accuracy': accuracy,
            'feature_importance': feature_importance,
            'confusion_matrix': cm
        }
    print("\nCountry Comparison Results:")
    for country in countries:
        print(f"\n{country}:")
        print(f"  Accuracy: {results[country]['accuracy']:.3f}")
        print(f"  Confusion Matrix:\n{results[country]['confusion_matrix']}")


    # --- Plotly: All countries confusion matrices in one HTML (2x2, Blues color) ---
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    fig_cm = make_subplots(rows=2, cols=2, subplot_titles=countries)
    zmax = max([results[c]['confusion_matrix'].max() for c in countries])
    for idx, country in enumerate(countries):
        cm = results[country]['confusion_matrix']
        row = idx // 2 + 1
        col = idx % 2 + 1
        # Draw heatmap
        heatmap = go.Heatmap(
            z=cm,
            x=['Pred 0', 'Pred 1'],
            y=['Actual 0', 'Actual 1'],
            colorscale='Blues',
            zmin=0,
            zmax=zmax,
            showscale=(idx==3),
            colorbar=dict(title='Count') if idx==3 else None,
            text=cm,
            texttemplate="",
            hovertemplate="Actual %{y}<br>Predicted %{x}<br>Count: %{z}<extra></extra>",
        )
        fig_cm.add_trace(heatmap, row=row, col=col)
        # Add white background, bold, large font annotations for each cell
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                fig_cm.add_annotation(
                    x=j,
                    y=i,
                    xref=f'x{idx+1}',
                    yref=f'y{idx+1}',
                    text=f"<b>{cm[i, j]}</b>",
                    showarrow=False,
                    font=dict(color="black", size=28, family="Arial Black, Arial, sans-serif"),
                    bgcolor="white",
                    opacity=0.95,
                    bordercolor="black",
                    borderwidth=2,
                    borderpad=4
                )
        # Draw all borders of the matrix (rectangle)
        fig_cm.add_shape(
            type="rect",
            xref=f'x{idx+1}',
            yref=f'y{idx+1}',
            x0=-0.5, x1=1.5, y0=-0.5, y1=1.5,
            line=dict(color="black", width=4),
            fillcolor="rgba(0,0,0,0)",
            layer="above"
        )
        # Draw inner cell borders (vertical and horizontal)
        fig_cm.add_shape(
            type="line",
            xref=f'x{idx+1}',
            yref=f'y{idx+1}',
            x0=0.5, x1=0.5, y0=-0.5, y1=1.5,
            line=dict(color="black", width=2),
            layer="above"
        )
        fig_cm.add_shape(
            type="line",
            xref=f'x{idx+1}',
            yref=f'y{idx+1}',
            x0=-0.5, x1=1.5, y0=0.5, y1=0.5,
            line=dict(color="black", width=2),
            layer="above"
        )
    fig_cm.update_layout(
        title_text="Medication Adherence Confusion Matrices by Country",
        height=800,
        width=1000,
        font=dict(size=16),
        plot_bgcolor="white"
    )
    fig_cm.write_html('models/singapore_models/adherence_confusion_matrix_comparison.html')

    # --- Plotly: All countries top 10 feature importances in one HTML (2x2) ---
    fig_feat = make_subplots(rows=2, cols=2, subplot_titles=countries, shared_yaxes=True)
    for idx, country in enumerate(countries):
        fi = results[country]['feature_importance'].head(10).sort_values('importance', ascending=True)
        row = idx // 2 + 1
        col = idx % 2 + 1
        bar = go.Bar(
            x=fi['importance'],
            y=fi['feature'],
            orientation='h',
            marker=dict(color=fi['importance'], colorscale='Viridis'),
            showlegend=False
        )
        fig_feat.add_trace(bar, row=row, col=col)
    fig_feat.update_layout(
        title_text="Top 10 Feature Importances for Medication Adherence by Country",
        height=900,
        width=1200,
        font=dict(size=16)
    )
    fig_feat.write_html('models/singapore_models/adherence_feature_importance_comparison.html')

    return results

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
        # Sanitize all string inputs from external data
        singapore_data['singapore_town'] = singapore_data['singapore_town'].apply(lambda x: sanitize_input(str(x)))
        demographics['town'] = demographics['town'].apply(lambda x: sanitize_input(str(x)))
        
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

        # Interactive Feature Importance Plot
        fig1 = px.bar(feature_importance.head(10), x='importance', y='feature', orientation='h',
                     title='Top 10 Features for Fall Risk', color='importance', color_continuous_scale='Viridis')
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        fig1.write_html('models/singapore_models/fall_feature_importance.html')

        # Interactive Predicted vs Actual Plot
        fig2 = px.scatter(x=y_test, y=y_pred, labels={'x':'Actual Fall Risk Score', 'y':'Predicted Fall Risk Score'},
                         title='Predicted vs Actual Fall Risk Score', opacity=0.7)
        fig2.add_shape(type='line', x0=min(y_test), y0=min(y_test), x1=max(y_test), y1=max(y_test),
                      line=dict(color='red', dash='dash'))
        fig2.write_html('models/singapore_models/fall_pred_vs_actual.html')

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
        # Sanitize user_id and other string fields
        singapore_data['user_id'] = singapore_data['user_id'].apply(lambda x: sanitize_input(str(x)) if 'user_id' in singapore_data.columns else x)
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

        # Interactive Confusion Matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred_binary)
        fig1 = px.imshow(
            cm,
            text_auto=True,
            color_continuous_scale='Viridis',
            labels=dict(x="Predicted", y="Actual", color="Count"),
            title="Confusion Matrix - Health Anomaly Detection"
        )
        fig1.update_traces(
            textfont=dict(color="black", size=32, family="Arial Black, Arial, sans-serif")
        )
        # Add white background annotations for each cell
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                fig1.add_annotation(
                    x=j,
                    y=i,
                    text=str(cm[i, j]),
                    showarrow=False,
                    font=dict(color="black", size=32, family="Arial Black, Arial, sans-serif"),
                    bgcolor="white",
                    opacity=0.9
                )
        fig1.update_layout(
            xaxis_title="Predicted",
            yaxis_title="Actual",
            font=dict(color="black", size=18),
            coloraxis_colorbar=dict(title="Count")
        )
        fig1.write_html('models/singapore_models/anomaly_confusion_matrix.html')

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
    
    # Model 1: Medication Adherence (Multi-country)
    print("\n1️⃣ MEDICATION ADHERENCE PREDICTION (Multi-country)")
    print("-" * 40)
    # Run multi-country comparison and print results
    adherence_results = compare_countries_adherence()
    # For summary, use Singapore's results
    results['adherence_accuracy'] = adherence_results['Singapore']['accuracy']
    results['adherence_features'] = adherence_results['Singapore']['feature_importance']
    
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

    print("\n📈 Interactive visualizations saved as HTML in models/singapore_models/:")
    print("   - adherence_feature_importance.html (Medication Adherence Features)")
    print("   - adherence_confusion_matrix.html (Medication Adherence Confusion Matrix)")
    print("   - fall_feature_importance.html (Fall Risk Features)")
    print("   - fall_pred_vs_actual.html (Fall Risk Predicted vs Actual)")
    print("   - anomaly_confusion_matrix.html (Health Anomaly Confusion Matrix)")

    print("\n📝 Conclusion:")
    print("This project demonstrates a robust AI-driven analytics pipeline for Singapore senior care, integrating multiple datasets, advanced ML models, and interactive visualizations. The system provides actionable insights for healthcare decision-makers and sets a foundation for future enhancements, such as real-time monitoring and deployment with real-world data.")

    return results

if __name__ == "__main__":
    main()
