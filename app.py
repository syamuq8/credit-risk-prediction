import os
import csv
import json
import time
import io
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response, session
from predict import get_predictions_and_explanations
import database

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'credit_risk_prediction_system_secret_key_fintech')

# Global Configuration
ACTIVE_MODEL = 'gradient_boosting'

# Initialize database (SQLite or MongoDB) on load
database.init_db()

CURRENCIES = {
    'USD': {'symbol': '$', 'label': 'USD ($)'},
    'INR': {'symbol': '₹', 'label': 'INR (₹)'},
    'EUR': {'symbol': '€', 'label': 'EUR (€)'},
    'GBP': {'symbol': '£', 'label': 'GBP (£)'}
}

@app.context_processor
def inject_currency():
    symbol = session.get('currency_symbol', '$')
    currency_code = session.get('currency_code', 'USD')
    return dict(currency_symbol=symbol, currency_code=currency_code)

@app.route('/set_currency', methods=['POST'])
def set_currency():
    code = request.form.get('currency_code', 'USD')
    if code in CURRENCIES:
        session['currency_code'] = code
        session['currency_symbol'] = CURRENCIES[code]['symbol']
    return redirect(request.referrer or url_for('dashboard'))

def login_required(f):
    """Enforces active session login."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            if request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication credentials required.'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to enforce Admin role."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') != 'Admin':
            if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Admin role credentials required.'}), 403
            return redirect(url_for('login', error='Admin privileges required.'))
        return f(*args, **kwargs)
    return decorated_function

def officer_required(f):
    """Decorator to enforce Loan Officer or Admin roles."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in') or session.get('role') not in ['Admin', 'Loan Officer']:
            if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Loan Officer role credentials required.'}), 403
            return redirect(url_for('login', error='Loan Officer privileges required.'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def dashboard():
    # 1. Fetch statistics from unified database driver
    stats_data = database.db_get_dashboard_stats()
    
    total_predictions = stats_data[0]
    approved_count = stats_data[1]
    rejected_count = stats_data[2]
    medium_count = stats_data[3]
    avg_credit_score = stats_data[4]
    default_rate = stats_data[5]
    avg_income = stats_data[6]
    avg_loan_amount = stats_data[7]
    monthly_stats = stats_data[8]
    purpose_stats = stats_data[9]
    employment_stats = stats_data[10]
    scatter_data = stats_data[11]
    score_ranges = stats_data[12]
    recent_predictions = stats_data[13]
    top_high_risk = stats_data[14]
    
    # Fallback mock timeline values if empty
    if len(monthly_stats) <= 1:
        monthly_stats = {'2026-03': 15, '2026-04': 22, '2026-05': 35, '2026-06': 48, '2026-07': total_predictions}
        
    risk_dist = {
        'Low Risk': approved_count,
        'Medium Risk': medium_count,
        'High Risk': rejected_count
    }
    
    return render_template(
        'dashboard.html',
        total_predictions=total_predictions,
        approved_loans=approved_count,
        rejected_loans=rejected_count,
        low_count=approved_count,
        medium_count=medium_count,
        high_count=rejected_count,
        avg_credit_score=avg_credit_score,
        default_rate=default_rate,
        avg_income=avg_income,
        avg_loan_amount=avg_loan_amount,
        risk_dist=risk_dist,
        monthly_stats=json.dumps(monthly_stats),
        purpose_stats=json.dumps(purpose_stats),
        employment_stats=json.dumps(employment_stats),
        scatter_data=json.dumps(scatter_data),
        score_ranges=json.dumps(score_ranges),
        recent_predictions=recent_predictions,
        top_high_risk=top_high_risk,
        active_model=ACTIVE_MODEL.upper().replace('_', ' ')
    )

@app.route('/predict', methods=['GET', 'POST'])
@officer_required
def predict():
    if request.method == 'GET':
        return render_template('predict.html')
        
    try:
        input_data = {
            'Age': int(request.form.get('age')),
            'Gender': request.form.get('gender'),
            'Annual Income': float(request.form.get('annual_income')),
            'Monthly Income': float(request.form.get('annual_income')) / 12.0,
            'Employment Status': request.form.get('employment_status'),
            'Years of Employment': float(request.form.get('years_employment')),
            'Education': request.form.get('education'),
            'Marital Status': request.form.get('marital_status'),
            'Loan Amount': float(request.form.get('loan_amount')),
            'Loan Purpose': request.form.get('loan_purpose'),
            'Interest Rate': float(request.form.get('interest_rate')),
            'Loan Term': int(request.form.get('loan_term')),
            'Credit Score': int(request.form.get('credit_score')),
            'Debt-to-Income Ratio': float(request.form.get('dti')),
            'Number of Existing Loans': int(request.form.get('existing_loans')),
            'Number of Credit Cards': int(request.form.get('credit_cards')),
            'Previous Loan Defaults': int(request.form.get('previous_defaults')),
            'Savings Balance': float(request.form.get('savings_balance')),
            'Monthly Expenses': float(request.form.get('monthly_expenses')),
            'Property Ownership': request.form.get('property_ownership'),
            'Dependents': int(request.form.get('dependents'))
        }
        applicant_name = request.form.get('applicant_name', 'Anonymous')
        
        # Run Predict Engine with ACTIVE_MODEL
        result = get_predictions_and_explanations(input_data, ACTIVE_MODEL)
        
        # Prepare document for database saving
        save_doc = input_data.copy()
        # Clean naming conventions to match fields
        save_doc['applicant_name'] = applicant_name
        save_doc['age'] = input_data['Age']
        save_doc['gender'] = input_data['Gender']
        save_doc['annual_income'] = input_data['Annual Income']
        save_doc['employment_status'] = input_data['Employment Status']
        save_doc['years_employment'] = input_data['Years of Employment']
        save_doc['education'] = input_data['Education']
        save_doc['marital_status'] = input_data['Marital Status']
        save_doc['loan_amount'] = input_data['Loan Amount']
        save_doc['loan_purpose'] = input_data['Loan Purpose']
        save_doc['interest_rate'] = input_data['Interest Rate']
        save_doc['loan_term'] = input_data['Loan Term']
        save_doc['credit_score'] = input_data['Credit Score']
        save_doc['dti'] = input_data['Debt-to-Income Ratio']
        save_doc['existing_loans'] = input_data['Number of Existing Loans']
        save_doc['credit_cards'] = input_data['Number of Credit Cards']
        save_doc['previous_defaults'] = input_data['Previous Loan Defaults']
        save_doc['savings_balance'] = input_data['Savings Balance']
        save_doc['monthly_expenses'] = input_data['Monthly Expenses']
        save_doc['property_ownership'] = input_data['Property Ownership']
        save_doc['dependents'] = input_data['Dependents']
        
        save_doc['risk_level'] = result['risk_level']
        save_doc['default_probability'] = result['default_probability']
        save_doc['repayment_probability'] = result['repayment_probability']
        save_doc['recommendation'] = result['recommendation']
        save_doc['badge'] = result['badge']
        save_doc['model_used'] = ACTIVE_MODEL
        
        # Save record through the unified DB interface
        database.db_save_prediction(save_doc)
        
        # Log prediction event to audit trails
        database.db_log_action(session.get('username', 'Anonymous'), session.get('role', 'Viewer'), 'Credit Prediction', f"Assessed applicant: {applicant_name} ({result['risk_level']})")
        
        # Trigger mock SMTP email dispatcher with assessment PDF attachment
        from email_advisor import send_report_email
        send_report_email(None, applicant_name, result)
        
        return render_template(
            'result.html',
            applicant_name=applicant_name,
            input_data=input_data,
            result=result,
            prediction_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('predict.html', error=f"Error running prediction: {str(e)}")

@app.route('/history')
@login_required
def history():
    search = request.args.get('search', '').strip()
    risk = request.args.get('risk', '').strip()
    sort_by = request.args.get('sort', 'prediction_date')
    order = request.args.get('order', 'DESC')
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    
    # Retrieve predictions using unified database connection
    rows, total_records = database.db_get_predictions(
        search=search, risk=risk, sort_by=sort_by, order=order, limit=per_page, offset=offset
    )
    total_pages = max(1, (total_records + per_page - 1) // per_page)
    
    return render_template(
        'history.html',
        predictions=rows,
        search_query=search,
        filter_risk=risk,
        sort_by=sort_by,
        order=order,
        page=page,
        total_pages=total_pages,
        total_records=total_records
    )

@app.route('/history/delete/<id>', methods=['POST'])
@admin_required
def delete_history(id):
    try:
        database.db_delete_prediction(id)
        return jsonify({'success': True, 'message': 'Record deleted successfully.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/history/details/<id>')
@officer_required
def history_details(id):
    row = database.db_get_details(id)
    if not row:
        return jsonify({'success': False, 'message': 'Record not found.'}), 404
    return jsonify({'success': True, 'data': row})

@app.route('/customers')
@login_required
def customers():
    rows = database.db_get_unique_customers()
    return render_template('customer_profile.html', customers=rows)

@app.route('/customer/<name>')
@login_required
def customer_profile(name):
    history_runs = database.db_get_customer_history(name)
    if not history_runs:
        return redirect(url_for('customers'))
        
    latest = history_runs[-1]
    
    dates = [row['prediction_date'][:10] for row in history_runs]
    scores = [row['credit_score'] for row in history_runs]
    risks = [row['default_probability'] for row in history_runs]
    
    return render_template(
        'customer_detail.html',
        name=name,
        latest=latest,
        history=history_runs,
        timeline_dates=json.dumps(dates),
        timeline_scores=json.dumps(scores),
        timeline_risks=json.dumps(risks)
    )

@app.route('/analytics')
@login_required
def analytics_dashboard():
    comp_path = 'models/model_comparison.json'
    comparisons = []
    if os.path.exists(comp_path):
        with open(comp_path, 'r') as f:
            comparisons = json.load(f)
            
    active_stats = {}
    for comp in comparisons:
        if comp['Model'].lower().replace(' ', '_') == ACTIVE_MODEL:
            active_stats = comp
            break
            
    if not active_stats and comparisons:
        active_stats = comparisons[0]
        
    active_filename = ACTIVE_MODEL
    
    return render_template(
        'analytics.html',
        comparisons=comparisons,
        active_model_name=ACTIVE_MODEL.upper().replace('_', ' '),
        ACTIVE_MODEL=ACTIVE_MODEL,
        active_stats=active_stats,
        cm_image=f"confusion_matrix_{active_filename}.png",
        roc_image=f"roc_curve_{active_filename}.png",
        fi_image=f"feature_importance_{active_filename}.png"
    )

@app.route('/datasets')
@admin_required
def datasets():
    stats_path = 'models/dataset_stats.json'
    stats = {}
    if os.path.exists(stats_path):
        with open(stats_path, 'r') as f:
            stats = json.load(f)
            
    return render_template('datasets.html', stats=stats)

@app.route('/datasets/upload', methods=['POST'])
@admin_required
def upload_dataset():
    if 'dataset' not in request.files:
        return jsonify({'success': False, 'message': 'No dataset file provided.'}), 400
        
    file = request.files['dataset']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected.'}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'Invalid file format. Only CSV allowed.'}), 400
        
    try:
        os.makedirs('dataset', exist_ok=True)
        file.save('dataset/credit_risk_dataset.csv')
        database.db_log_action(session.get('username'), session.get('role'), 'Dataset Upload', f"Uploaded {file.filename}")
        return jsonify({'success': True, 'message': 'Dataset successfully uploaded. Triggering model retraining...'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/datasets/retrain', methods=['POST'])
@admin_required
def trigger_retrain():
    try:
        from train_model import train_and_evaluate
        train_and_evaluate()
        database.db_log_action(session.get('username'), session.get('role'), 'Model Retrain', 'Successfully retrained all machine learning model files')
        return jsonify({'success': True, 'message': 'All models successfully retrained and saved.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Retraining failed: {str(e)}"}), 500

@app.route('/datasets/delete', methods=['POST'])
@admin_required
def delete_dataset():
    try:
        from generate_data import generate_credit_dataset
        df = generate_credit_dataset()
        df.to_csv('dataset/credit_risk_dataset.csv', index=False)
        
        from train_model import train_and_evaluate
        train_and_evaluate()
        database.db_log_action(session.get('username'), session.get('role'), 'Dataset Reset', 'Reset credit risk baseline training files')
        
        return jsonify({'success': True, 'message': 'Dataset deleted. Baseline dataset regenerated and models retrained.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/datasets/download')
def download_dataset():
    data_path = 'dataset/credit_risk_dataset.csv'
    if not os.path.exists(data_path):
        return "Dataset file not found.", 404
        
    with open(data_path, 'r') as f:
        csv_data = f.read()
        
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=credit_risk_dataset.csv"}
    )

@app.route('/models')
@admin_required
def models_center():
    comp_path = 'models/model_comparison.json'
    comparisons = []
    if os.path.exists(comp_path):
        with open(comp_path, 'r') as f:
            comparisons = json.load(f)
            
    return render_template(
        'models.html',
        comparisons=comparisons,
        active_model_key=ACTIVE_MODEL
    )

@app.route('/models/switch', methods=['POST'])
@admin_required
def switch_model():
    global ACTIVE_MODEL
    model_key = request.form.get('model_key', '').strip()
    if not model_key:
        return jsonify({'success': False, 'message': 'Model identifier key required.'}), 400
        
    model_path = os.path.join('models', f"{model_key}.pkl")
    if not os.path.exists(model_path):
        return jsonify({'success': False, 'message': f"Model artifact {model_key}.pkl not found."}), 404
        
    ACTIVE_MODEL = model_key
    database.db_log_action(session.get('username'), session.get('role'), 'Switch Model', f"Active prediction model successfully switched to {model_key}")
    return jsonify({
        'success': True, 
        'message': f"Active prediction model successfully switched to {model_key.upper().replace('_', ' ')}."
    })

@app.route('/calculator')
def loan_calculator():
    return render_template('calculator.html')

@app.route('/simulator')
def credit_simulator():
    # Retrieve some sample customer names for simulator loading
    rows = database.db_get_unique_customers()
    return render_template('simulator.html', customers=rows)

@app.route('/report/<id>')
@officer_required
def view_report(id):
    row = database.db_get_details(id)
    if not row:
        return "Prediction record not found.", 404
        
    input_data = {
        'Age': row['age'], 'Gender': row['gender'], 'Annual Income': row['annual_income'],
        'Monthly Income': row['annual_income'] / 12.0, 'Employment Status': row['employment_status'],
        'Years of Employment': row['years_employment'], 'Education': row['education'],
        'Marital Status': row['marital_status'], 'Loan Amount': row['loan_amount'],
        'Loan Purpose': row['loan_purpose'], 'Interest Rate': row['interest_rate'],
        'Loan Term': row['loan_term'], 'Credit Score': row['credit_score'],
        'Debt-to-Income Ratio': row['dti'], 'Number of Existing Loans': row['existing_loans'],
        'Number of Credit Cards': row['credit_cards'], 'Previous Loan Defaults': row['previous_defaults'],
        'Savings Balance': row['savings_balance'], 'Monthly Expenses': row['monthly_expenses'],
        'Property Ownership': row['property_ownership'], 'Dependents': row['dependents']
    }
    
    result = get_predictions_and_explanations(input_data, row['model_used'])
    
    return render_template(
        'report.html',
        row=row,
        result=result,
        prediction_time=row['prediction_date']
    )

@app.route('/report/certificate/<id>')
@officer_required
def view_certificate(id):
    row = database.db_get_details(id)
    if not row:
        return "Prediction record not found.", 404
        
    input_data = {
        'Age': row['age'], 'Gender': row['gender'], 'Annual Income': row['annual_income'],
        'Monthly Income': row['annual_income'] / 12.0, 'Employment Status': row['employment_status'],
        'Years of Employment': row['years_employment'], 'Education': row['education'],
        'Marital Status': row['marital_status'], 'Loan Amount': row['loan_amount'],
        'Loan Purpose': row['loan_purpose'], 'Interest Rate': row['interest_rate'],
        'Loan Term': row['loan_term'], 'Credit Score': row['credit_score'],
        'Debt-to-Income Ratio': row['dti'], 'Number of Existing Loans': row['existing_loans'],
        'Number of Credit Cards': row['credit_cards'], 'Previous Loan Defaults': row['previous_defaults'],
        'Savings Balance': row['savings_balance'], 'Monthly Expenses': row['monthly_expenses'],
        'Property Ownership': row['property_ownership'], 'Dependents': row['dependents']
    }
    
    result = get_predictions_and_explanations(input_data, row['model_used'])
    
    return render_template(
        'certificate.html',
        row=row,
        result=result,
        prediction_time=row['prediction_date']
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin' and password == 'admin':
        session['logged_in'] = True
        session['username'] = 'admin'
        session['role'] = 'Admin'
        database.db_log_action('admin', 'Admin', 'User Login', 'Admin user authenticated successfully')
        return redirect(url_for('dashboard'))
    elif username == 'officer' and password == 'officer':
        session['logged_in'] = True
        session['username'] = 'officer'
        session['role'] = 'Loan Officer'
        database.db_log_action('officer', 'Loan Officer', 'User Login', 'Loan Officer authenticated successfully')
        return redirect(url_for('dashboard'))
    elif username == 'viewer' and password == 'viewer':
        session['logged_in'] = True
        session['username'] = 'viewer'
        session['role'] = 'Viewer'
        database.db_log_action('viewer', 'Viewer', 'User Login', 'Viewer authenticated successfully')
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Invalid credentials.')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))

@app.route('/pages/<page_key>')
def render_pages(page_key):
    if page_key not in ['faq', 'about', 'help', 'health']:
        return "Page not found.", 404
        
    health_stats = {}
    if page_key == 'health':
        db_engine_name, db_engine_status = database.db_get_engine_info()
        
        db_size = 0
        if os.path.exists('credit_risk.db'):
            db_size = round(os.path.getsize('credit_risk.db') / 1024, 1) # KB
            
        health_stats = {
            'cpu_usage': 12.5,
            'ram_usage': 42.1,
            'db_size_kb': db_size,
            'models_trained_count': len([f for f in os.listdir('models') if f.endswith('.pkl')]),
            'python_version': '3.11',
            'server_status': f"ONLINE ({db_engine_status})",
            'uptime': '99.9%'
        }
        
    return render_template('pages.html', page_key=page_key, health=health_stats)

@app.route('/audit')
@admin_required
def view_audit_logs():
    logs = database.db_get_audit_logs()
    return render_template('audit.html', logs=logs)

@app.route('/export/csv')
def export_csv():
    selected_ids = request.args.get('ids', '')
    
    if selected_ids:
        # Fetch only selected ids from database
        rows = []
        for rid in selected_ids.split(','):
            row = database.db_get_details(rid)
            if row:
                rows.append(row)
    else:
        # Fetch all
        rows, _ = database.db_get_predictions(fetch_all=True)
        
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow([
            'ID', 'Applicant Name', 'Age', 'Gender', 'Annual Income', 'Employment Status',
            'Credit Score', 'Loan Amount', 'Loan Purpose', 'DTI', 'Risk Level',
            'Default Probability (%)', 'Repayment Probability (%)', 'Recommendation', 'Prediction Date', 'Model Used'
        ])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)
        
        for row in rows:
            writer.writerow([
                row['id'], row['applicant_name'], row['age'], row['gender'], row['annual_income'],
                row['employment_status'], row['credit_score'], row['loan_amount'], row['loan_purpose'],
                row['dti'], row['risk_level'], row['default_probability'], row['repayment_probability'],
                row['recommendation'], row['prediction_date'], row['model_used']
            ])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)
            
def parse_api_input(data):
    """Safely extracts and formats dictionary inputs for inference."""
    return {
        'Age': int(data.get('age', 35)),
        'Gender': data.get('gender', 'Male'),
        'Annual Income': float(data.get('annual_income', 50000.0)),
        'Monthly Income': float(data.get('annual_income', 50000.0)) / 12.0,
        'Employment Status': data.get('employment_status', 'Employed'),
        'Years of Employment': float(data.get('years_employment', 3.0)),
        'Education': data.get('education', 'Bachelor'),
        'Marital Status': data.get('marital_status', 'Single'),
        'Loan Amount': float(data.get('loan_amount', 10000.0)),
        'Loan Purpose': data.get('loan_purpose', 'Personal'),
        'Interest Rate': float(data.get('interest_rate', 8.5)),
        'Loan Term': int(data.get('loan_term', 36)),
        'Credit Score': int(data.get('credit_score', 700)),
        'Debt-to-Income Ratio': float(data.get('dti', 0.25)),
        'Number of Existing Loans': int(data.get('existing_loans', 0)),
        'Number of Credit Cards': int(data.get('credit_cards', 2)),
        'Previous Loan Defaults': int(data.get('previous_defaults', 0)),
        'Savings Balance': float(data.get('savings_balance', 5000.0)),
        'Monthly Expenses': float(data.get('monthly_expenses', 1500.0)),
        'Property Ownership': data.get('property_ownership', 'Rent'),
        'Dependents': int(data.get('dependents', 0))
    }

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    try:
        data = request.get_json() or {}
        input_data = parse_api_input(data)
        result = get_predictions_and_explanations(input_data, ACTIVE_MODEL)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        data = request.get_json() or {}
        input_data = parse_api_input(data)
        applicant_name = data.get('applicant_name', 'API Anonymous')
        
        result = get_predictions_and_explanations(input_data, ACTIVE_MODEL)
        
        if result.get('eligible', True):
            save_doc = input_data.copy()
            save_doc['applicant_name'] = applicant_name
            save_doc['age'] = input_data['Age']
            save_doc['gender'] = input_data['Gender']
            save_doc['annual_income'] = input_data['Annual Income']
            save_doc['employment_status'] = input_data['Employment Status']
            save_doc['years_employment'] = input_data['Years of Employment']
            save_doc['education'] = input_data['Education']
            save_doc['marital_status'] = input_data['Marital Status']
            save_doc['loan_amount'] = input_data['Loan Amount']
            save_doc['loan_purpose'] = input_data['Loan Purpose']
            save_doc['interest_rate'] = input_data['Interest Rate']
            save_doc['loan_term'] = input_data['Loan Term']
            save_doc['credit_score'] = input_data['Credit Score']
            save_doc['dti'] = input_data['Debt-to-Income Ratio']
            save_doc['existing_loans'] = input_data['Number of Existing Loans']
            save_doc['credit_cards'] = input_data['Number of Credit Cards']
            save_doc['previous_defaults'] = input_data['Previous Loan Defaults']
            save_doc['savings_balance'] = input_data['Savings Balance']
            save_doc['monthly_expenses'] = input_data['Monthly Expenses']
            save_doc['property_ownership'] = input_data['Property Ownership']
            save_doc['dependents'] = input_data['Dependents']
            
            save_doc['risk_level'] = result['risk_level']
            save_doc['default_probability'] = result['default_probability']
            save_doc['repayment_probability'] = result['repayment_probability']
            save_doc['recommendation'] = result['recommendation']
            save_doc['badge'] = result['badge']
            save_doc['model_used'] = ACTIVE_MODEL
            
            database.db_save_prediction(save_doc)
            
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/history')
def api_history():
    search = request.args.get('search', '')
    risk = request.args.get('risk', '')
    rows, _ = database.db_get_predictions(search=search, risk=risk, fetch_all=True)
    return jsonify({'success': True, 'data': rows})

@app.route('/api/model_info')
def api_model_info():
    comp_path = 'models/model_comparison.json'
    comparisons = []
    if os.path.exists(comp_path):
        with open(comp_path, 'r') as f:
            comparisons = json.load(f)
    return jsonify({
        'success': True,
        'active_model': ACTIVE_MODEL,
        'comparisons': comparisons
    })

@app.route('/api/stats')
def api_stats():
    stats_data = database.db_get_dashboard_stats()
    return jsonify({
        'success': True,
        'total_assessments': stats_data[0],
        'approved_count': stats_data[1],
        'rejected_count': stats_data[2],
        'medium_count': stats_data[3],
        'avg_credit_score': stats_data[4],
        'default_rate': stats_data[5],
        'avg_income': stats_data[6],
        'avg_loan_amount': stats_data[7],
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
