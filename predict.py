import os
import time
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = 'models'
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, 'preprocessor.pkl')

def check_eligibility(d):
    """Checks basic banking pre-qualification criteria."""
    reasons = []
    
    # Age Check
    age = d.get('Age', 0)
    if age < 18 or age > 80:
        reasons.append("Applicant age must be between 18 and 80 years.")
        
    # Income Check
    income = d.get('Annual Income', 0.0)
    if income < 10000.0:
        reasons.append("Annual income is below the minimum required threshold of $10,000.")
        
    # Credit Score Check
    fico = d.get('Credit Score', 0)
    if fico < 300 or fico > 850:
        reasons.append("FICO Credit Score must be between 300 and 850.")
        
    return len(reasons) == 0, reasons

def detect_fraud_anomaly(d):
    """Scans for logical parameter conflicts indicating potential fraud."""
    flags = []
    
    # Age vs Employment
    age = d.get('Age', 0)
    employment_yrs = d.get('Years of Employment', 0.0)
    if age - employment_yrs < 14:
        flags.append("Logical Conflict: Employment length is impossible for applicant age.")
        
    # Unemployed with excessive income & zero savings
    emp_status = d.get('Employment Status', '')
    savings = d.get('Savings Balance', 0.0)
    income = d.get('Annual Income', 0.0)
    if emp_status == 'Unemployed' and savings == 0.0 and income > 100000.0:
        flags.append("Anomaly: Unemployed applicant with zero savings reporting > $100k annual income.")
        
    # Extreme DTI with no buffer
    dti = d.get('Debt-to-Income Ratio', 0.0)
    if dti > 0.95 and savings < 100.0:
        flags.append("Anomaly: Extreme Debt-to-Income (DTI) ratio with zero savings reserve.")
        
    return len(flags) > 0, flags

def get_predictions_and_explanations(input_data, model_key='gradient_boosting'):
    """
    Infers credit risk using the specified active model.
    """
    start_time = time.time()
    
    # 0. Check Eligibility Pre-qualification
    is_eligible, reasons = check_eligibility(input_data)
    if not is_eligible:
        return {
            'risk_level': 'Ineligible',
            'default_probability': 100.0,
            'repayment_probability': 0.0,
            'confidence_score': 100.0,
            'recommendation': 'Reject',
            'badge': 'danger',
            'explanations': [f"Pre-qualification failed: {', '.join(reasons)}"],
            'positive_drivers': [],
            'negative_drivers': [],
            'suggestions': ["Correct parameters and re-apply once eligibility requirements are met."],
            'contributions': [],
            'duration_ms': 0.0,
            'eligible': False,
            'ineligible_reasons': reasons,
            'fraud_flag': False,
            'fraud_reasons': []
        }
        
    
    # 1. Load Preprocessor and Model
    if not os.path.exists(PREPROCESSOR_PATH):
        raise FileNotFoundError("Preprocessor metadata not found. Please run train_model.py first.")
        
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    
    # Map model key to filename
    model_filename = f"{model_key}.pkl"
    model_path = os.path.join(MODEL_DIR, model_filename)
    
    # Fallback to general model if specified model not found
    if not os.path.exists(model_path):
        model_path = os.path.join(MODEL_DIR, 'credit_model.pkl')
        
    model = joblib.load(model_path)
    
    # 2. Format Input
    df_raw = pd.DataFrame([input_data])
    num_cols = preprocessor['num_cols']
    cat_cols = preprocessor['cat_cols']
    target_mapping = preprocessor['target_mapping']
    inverse_target_mapping = preprocessor['inverse_target_mapping']
    
    all_features = num_cols + cat_cols
    for col in all_features:
        if col not in df_raw.columns:
            df_raw[col] = np.nan
    df_raw = df_raw[all_features]
    
    # Impute
    num_imputer = preprocessor['num_imputer']
    cat_imputer = preprocessor['cat_imputer']
    
    df_num_imputed = pd.DataFrame(num_imputer.transform(df_raw[num_cols]), columns=num_cols)
    df_cat_imputed = pd.DataFrame(cat_imputer.transform(df_raw[cat_cols]), columns=cat_cols)
    
    # Scale & Encode
    scaler = preprocessor['scaler']
    encoder = preprocessor['encoder']
    
    cat_encoded = encoder.transform(df_cat_imputed)
    encoded_cat_names = encoder.get_feature_names_out(cat_cols)
    df_cat_encoded = pd.DataFrame(cat_encoded, columns=encoded_cat_names)
    
    num_scaled = scaler.transform(df_num_imputed)
    df_num_scaled = pd.DataFrame(num_scaled, columns=num_cols)
    
    df_processed = pd.concat([df_num_scaled, df_cat_encoded], axis=1)
    
    # 3. Prediction
    prediction_code = model.predict(df_processed)[0]
    probabilities = model.predict_proba(df_processed)[0]
    
    risk_level = inverse_target_mapping[prediction_code]
    p_low, p_med, p_high = probabilities[0], probabilities[1], probabilities[2]
    
    default_prob = float(round((p_high + 0.3 * p_med) * 100, 1))
    repay_prob = float(round(100.0 - default_prob, 1))
    confidence_score = float(round(probabilities[prediction_code] * 100, 1))
    
    # Recommendations
    if risk_level == 'Low Risk':
        recommendation = "Approve"
        badge = "success"
    elif risk_level == 'Medium Risk':
        recommendation = "Manual Review"
        badge = "warning"
    else:
        recommendation = "Reject"
        badge = "danger"
        
    # 4. Feature Attributions (XAI / SHAP Fallback Approximation)
    feature_directions = {
        'Credit Score': -1, 'Debt-to-Income Ratio': 1, 'Previous Loan Defaults': 1,
        'Savings Balance': -1, 'Annual Income': -1, 'Loan Amount': 1, 'Interest Rate': 1,
        'Age': -1, 'Years of Employment': -1, 'Monthly Expenses': 1,
        'Number of Existing Loans': 1, 'Number of Credit Cards': 1, 'Dependents': 1, 'Loan Term': 1
    }
    
    feature_importances = {}
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        for name, imp in zip(df_processed.columns, importances):
            orig_name = name
            for cat_col in cat_cols:
                if name.startswith(cat_col + '_'):
                    orig_name = cat_col
                    break
            feature_importances[orig_name] = feature_importances.get(orig_name, 0) + imp
    elif hasattr(model, 'coef_'):
        importances = np.mean(np.abs(model.coef_), axis=0)
        for name, imp in zip(df_processed.columns, importances):
            orig_name = name
            for cat_col in cat_cols:
                if name.startswith(cat_col + '_'):
                    orig_name = cat_col
                    break
            feature_importances[orig_name] = feature_importances.get(orig_name, 0) + imp
    else:
        feature_importances = {col: 1.0 / len(all_features) for col in all_features}
        
    total_imp = sum(feature_importances.values())
    if total_imp > 0:
        feature_importances = {k: v / total_imp for k, v in feature_importances.items()}
        
    contributions = []
    # Numerical
    for col in num_cols:
        val = df_raw[col].iloc[0]
        if pd.isna(val):
            val = num_imputer.statistics_[num_cols.index(col)]
        idx = num_cols.index(col)
        mean_val = scaler.mean_[idx]
        std_val = scaler.scale_[idx]
        z_score = (val - mean_val) / std_val if std_val > 0 else 0
        
        imp = feature_importances.get(col, 0.05)
        dir_sign = feature_directions.get(col, 1)
        contrib = z_score * imp * dir_sign
        
        contributions.append({
            'feature': col,
            'value': float(val),
            'contribution': float(contrib),
            'formatted_val': f"{val:,}" if col in ['Annual Income', 'Monthly Income', 'Loan Amount', 'Savings Balance', 'Monthly Expenses'] else str(val)
        })
        
    # Categorical
    for col in cat_cols:
        val = df_raw[col].iloc[0]
        if pd.isna(val):
            val = cat_imputer.statistics_[cat_cols.index(col)]
        
        imp = feature_importances.get(col, 0.04)
        contrib = 0.0
        if col == 'Employment Status':
            contrib = 1.2 * imp if val == 'Unemployed' else (-0.4 * imp if val == 'Employed' else 0.0)
        elif col == 'Property Ownership':
            contrib = 0.4 * imp if val == 'Rent' else (-0.4 * imp if val == 'Own' else 0.0)
        elif col == 'Education':
            contrib = -0.3 * imp if val in ['Master', 'Doctorate'] else (0.3 * imp if val == 'High School' else 0.0)
            
        contributions.append({
            'feature': col,
            'value': val,
            'contribution': float(contrib),
            'formatted_val': str(val)
        })
        
    # Sort
    contributions = sorted(contributions, key=lambda x: x['contribution'], reverse=True)
    
    # Split drivers (up to 5 positive, 5 negative)
    positive_drivers = [c for c in contributions if c['contribution'] > 0.005][:5]
    negative_drivers = [c for c in sorted(contributions, key=lambda x: x['contribution']) if c['contribution'] < -0.005][:5]
    
    # If empty, fill default
    if not positive_drivers:
        positive_drivers = [{'feature': 'General profile indicators', 'value': 'Standard', 'contribution': 0.01, 'formatted_val': 'Standard'}]
    if not negative_drivers:
        negative_drivers = [{'feature': 'General credit status', 'value': 'Good', 'contribution': -0.01, 'formatted_val': 'Good'}]
        
    # Natural Language explanations
    explanation_sentences = []
    
    c_score = df_raw['Credit Score'].iloc[0]
    c_score = num_imputer.statistics_[num_cols.index('Credit Score')] if pd.isna(c_score) else c_score
    
    inc_val = df_raw['Annual Income'].iloc[0]
    inc_val = num_imputer.statistics_[num_cols.index('Annual Income')] if pd.isna(inc_val) else inc_val
    
    dti_val = df_raw['Debt-to-Income Ratio'].iloc[0]
    dti_val = num_imputer.statistics_[num_cols.index('Debt-to-Income Ratio')] if pd.isna(dti_val) else dti_val
    
    emp_s = df_raw['Employment Status'].iloc[0]
    emp_s = cat_imputer.statistics_[cat_cols.index('Employment Status')] if pd.isna(emp_s) else emp_s
    
    if risk_level == 'Low Risk':
        explanation_sentences.append(
            f"The applicant has a high annual income of ${inc_val:,.0f}, stable employment, and a strong credit score of {int(c_score)}, "
            f"resulting in a low probability of default."
        )
    elif risk_level == 'Medium Risk':
        explanation_sentences.append(
            f"The applicant shows moderate credit standings (Credit Score: {int(c_score)}) but has elevated monthly debt levels (DTI: {dti_val:.2f}) "
            f"which requires conditional verification or manual review."
        )
    else:
        explanation_sentences.append(
            f"The applicant presents high default risk factors, driven by a low credit score of {int(c_score)}, an excessive "
            f"Debt-to-Income ratio of {dti_val:.2f}, or previous default history."
        )
        
    # Suggestions Engine
    suggestions = []
    prev_defaults = df_raw['Previous Loan Defaults'].iloc[0]
    savings = df_raw['Savings Balance'].iloc[0]
    loan_amount = df_raw['Loan Amount'].iloc[0]
    existing_loans = df_raw['Number of Existing Loans'].iloc[0]
    years_employment = df_raw['Years of Employment'].iloc[0]
    
    # Fallbacks
    prev_defaults = 0 if pd.isna(prev_defaults) else prev_defaults
    savings = 0 if pd.isna(savings) else savings
    loan_amount = 5000 if pd.isna(loan_amount) else loan_amount
    existing_loans = 0 if pd.isna(existing_loans) else existing_loans
    years_employment = 0.0 if pd.isna(years_employment) else years_employment
    
    if c_score < 670:
        suggestions.append("Focus on increasing your credit score by making consistent on-time payments and resolving collection accounts.")
    if dti_val > 0.40:
        suggestions.append("Reduce outstanding monthly debts (credit cards, personal loans) to bring your Debt-to-Income (DTI) ratio below 35%.")
    if loan_amount > 0.40 * inc_val:
        suggestions.append(f"Decrease requested loan amount below ${inc_val * 0.3:,.0f} to lower the debt burden ratio.")
    if savings < 0.15 * loan_amount:
        suggestions.append("Increase your savings balance to establish a solid financial safety margin.")
    if emp_s in ['Unemployed', 'Self-Employed'] and years_employment < 2.0:
        suggestions.append("Improve employment stability by maintaining continuous tenure with a single employer for at least 1-2 years.")
    if existing_loans >= 3:
        suggestions.append("Avoid multiple concurrent active loans; consolidate your existing accounts before reapplying.")
        
    if not suggestions:
        suggestions.append("Maintain your strong credit parameters by keeping balances low and monitoring your FICO reports.")
        
    # Convert top contributions for UI SHAP force plot visualizer
    shap_visualizer = []
    # Send top 6 features to represent the waterfall vectors
    for c in contributions[:6]:
        shap_visualizer.append({
            'feature': c['feature'],
            'value': c['formatted_val'],
            'contribution': round(c['contribution'] * 100, 2)
        })
        
    duration_ms = round((time.time() - start_time) * 1000, 2)
    
    # Check Fraud Anomaly Detection
    is_anomaly, flags = detect_fraud_anomaly(input_data)
    
    res = {
        'risk_level': risk_level,
        'default_probability': default_prob,
        'repayment_probability': repay_prob,
        'confidence_score': confidence_score,
        'recommendation': recommendation,
        'badge': badge,
        'explanations': explanation_sentences,
        'positive_drivers': positive_drivers,
        'negative_drivers': negative_drivers,
        'suggestions': suggestions,
        'contributions': shap_visualizer,
        'duration_ms': duration_ms,
        'eligible': True,
        'ineligible_reasons': [],
        'fraud_flag': is_anomaly,
        'fraud_reasons': flags
    }
    
    if is_anomaly:
        res['recommendation'] = "Manual Review"
        res['badge'] = "warning"
        res['explanations'].insert(0, f"FRAUD ALERT: Suspicious application parameters detected. {', '.join(flags)}")
        
    return res
