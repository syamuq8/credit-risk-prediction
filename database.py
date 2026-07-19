import os
import sqlite3
import datetime
from bson import ObjectId

# Try to import pymongo, handle if not installed
try:
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    pymongo_available = True
except ImportError:
    pymongo_available = False

# Read from environment variables if present, otherwise default to local probing
ENV_DB_ENGINE = os.environ.get('DB_ENGINE', '').lower()
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'credit_risk_db')
SQLITE_PATH = 'credit_risk.db'

# Attempt MongoDB Connection
mongo_client = None
mongo_db = None

if pymongo_available and ENV_DB_ENGINE != 'sqlite':
    try:
        # Check connection status with a 2.0-second timeout
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        mongo_client.server_info() # Will trigger error if server is not running
        mongo_db = mongo_client[DB_NAME]
        DB_ENGINE = 'mongodb'
        print(">>> Database Connection: MongoDB connected successfully.")
    except (ServerSelectionTimeoutError, Exception) as e:
        if ENV_DB_ENGINE == 'mongodb':
            print(f">>> Database Connection Warning: MongoDB was requested but connection failed ({str(e)}). Falling back to SQLite.")
        else:
            print(f">>> Database Connection: MongoDB auto-probe failed. Falling back to SQLite.")
        DB_ENGINE = 'sqlite'
else:
    DB_ENGINE = 'sqlite'

def get_sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Mock seed dataset
seed_records = [
    ("Jane Harrison", 42, "Female", 98000.0, "Employed", 12.0, "Master", "Married", 15000.0, "Home Improvement", 5.5, 36, 810, 0.12, 0, 4, 0, 45000.0, 2200.0, "Own", 1, "Low Risk", 0.5, 99.5, "Approve", "success", "gradient_boosting", "2026-06-01 10:00:00"),
    ("Jane Harrison", 42, "Female", 98000.0, "Employed", 12.0, "Master", "Married", 15000.0, "Home Improvement", 5.5, 36, 790, 0.14, 0, 4, 0, 42000.0, 2200.0, "Own", 1, "Low Risk", 1.2, 98.8, "Approve", "success", "gradient_boosting", "2026-07-01 11:30:00"),
    ("Marcus Brody", 29, "Male", 54000.0, "Self-Employed", 3.5, "Bachelor", "Single", 20000.0, "Debt Consolidation", 12.5, 60, 640, 0.36, 1, 5, 0, 3500.0, 1600.0, "Rent", 0, "Medium Risk", 35.8, 64.2, "Manual Review", "warning", "gradient_boosting", "2026-05-10 14:15:00"),
    ("Marcus Brody", 29, "Male", 54000.0, "Self-Employed", 3.8, "Bachelor", "Single", 18000.0, "Debt Consolidation", 11.0, 60, 665, 0.32, 1, 5, 0, 6000.0, 1500.0, "Rent", 0, "Low Risk", 18.5, 81.5, "Approve", "success", "gradient_boosting", "2026-07-10 09:20:00"),
    ("Victor Vance", 36, "Male", 28000.0, "Unemployed", 0.5, "High School", "Divorced", 40000.0, "Business", 21.0, 60, 480, 0.62, 3, 8, 2, 200.0, 2100.0, "Rent", 3, "High Risk", 100.0, 0.0, "Reject", "danger", "gradient_boosting", "2026-07-15 15:40:00"),
    ("John Doe", 34, "Male", 75000.0, "Employed", 8.0, "Bachelor", "Married", 25000.0, "Home Improvement", 6.5, 36, 780, 0.18, 0, 4, 0, 15000.0, 2000.0, "Mortgage", 2, "Low Risk", 4.2, 95.8, "Approve", "success", "gradient_boosting", "2026-07-02 12:00:00"),
    ("Emma Watson", 52, "Female", 125000.0, "Employed", 15.0, "Doctorate", "Married", 50000.0, "Business", 4.5, 60, 820, 0.15, 1, 6, 0, 75000.0, 3500.0, "Own", 0, "Low Risk", 0.8, 99.2, "Approve", "success", "gradient_boosting", "2026-07-04 16:30:00"),
    ("Alice Smith", 28, "Female", 48000.0, "Employed", 4.0, "Associate", "Single", 12000.0, "Debt Consolidation", 9.5, 24, 690, 0.25, 0, 3, 0, 8000.0, 1400.0, "Rent", 0, "Low Risk", 9.4, 90.6, "Approve", "success", "gradient_boosting", "2026-07-06 09:15:00"),
    ("Robert Johnson", 45, "Male", 32000.0, "Unemployed", 0.0, "High School", "Divorced", 8000.0, "Personal", 18.5, 12, 510, 0.48, 2, 5, 1, 500.0, 1700.0, "Rent", 1, "High Risk", 82.5, 17.5, "Reject", "danger", "gradient_boosting", "2026-07-08 14:22:00"),
    ("Sophia Brown", 60, "Female", 85000.0, "Retired", 25.0, "Master", "Widowed", 20000.0, "Education", 7.0, 36, 750, 0.20, 0, 4, 0, 30000.0, 2500.0, "Own", 0, "Low Risk", 3.5, 96.5, "Approve", "success", "gradient_boosting", "2026-07-12 11:10:00"),
    ("James Wilson", 38, "Male", 62000.0, "Self-Employed", 6.0, "Bachelor", "Married", 35000.0, "Business", 14.5, 60, 590, 0.45, 2, 7, 0, 4000.0, 2800.0, "Rent", 2, "High Risk", 65.4, 34.6, "Reject", "danger", "gradient_boosting", "2026-07-13 13:45:00"),
    ("David Miller", 22, "Male", 35000.0, "Employed", 1.5, "High School", "Single", 6000.0, "Auto", 12.0, 24, 620, 0.28, 1, 3, 0, 2000.0, 1100.0, "Rent", 0, "Medium Risk", 33.2, 66.8, "Manual Review", "warning", "gradient_boosting", "2026-07-14 10:05:00"),
    ("Charlotte White", 43, "Female", 55000.0, "Employed", 9.0, "Bachelor", "Married", 18000.0, "Home Improvement", 8.5, 36, 710, 0.24, 1, 4, 0, 11000.0, 1800.0, "Mortgage", 2, "Low Risk", 6.8, 93.2, "Approve", "success", "gradient_boosting", "2026-07-16 16:12:00")
]

def init_db():
    """Initializes SQLite predictions table or seeds MongoDB collections if empty."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        if predictions_col.count_documents({}) == 0:
            print(">>> Seeding MongoDB with mock prediction history...")
            docs = []
            for r in seed_records:
                docs.append({
                    "applicant_name": r[0], "age": r[1], "gender": r[2], "annual_income": r[3], "employment_status": r[4],
                    "years_employment": r[5], "education": r[6], "marital_status": r[7], "loan_amount": r[8], "loan_purpose": r[9],
                    "interest_rate": r[10], "loan_term": r[11], "credit_score": r[12], "dti": r[13], "existing_loans": r[14],
                    "credit_cards": r[15], "previous_defaults": r[16], "savings_balance": r[17], "monthly_expenses": r[18],
                    "property_ownership": r[19], "dependents": r[20], "risk_level": r[21], "default_probability": r[22],
                    "repayment_probability": r[23], "recommendation": r[24], "badge": r[25], "model_used": r[26],
                    "prediction_date": r[27]
                })
            predictions_col.insert_many(docs)
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS predictions")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                annual_income REAL,
                employment_status TEXT,
                years_employment REAL,
                education TEXT,
                marital_status TEXT,
                loan_amount REAL,
                loan_purpose TEXT,
                interest_rate REAL,
                loan_term INTEGER,
                credit_score INTEGER,
                dti REAL,
                existing_loans INTEGER,
                credit_cards INTEGER,
                previous_defaults INTEGER,
                savings_balance REAL,
                monthly_expenses REAL,
                property_ownership TEXT,
                dependents INTEGER,
                risk_level TEXT,
                default_probability REAL,
                repayment_probability REAL,
                recommendation TEXT,
                badge TEXT,
                model_used TEXT,
                prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM predictions")
        if cursor.fetchone()[0] == 0:
            print(">>> Seeding SQLite database with mock prediction history...")
            cursor.executemany('''
                INSERT INTO predictions (
                    applicant_name, age, gender, annual_income, employment_status,
                    years_employment, education, marital_status, loan_amount, loan_purpose,
                    interest_rate, loan_term, credit_score, dti, existing_loans,
                    credit_cards, previous_defaults, savings_balance, monthly_expenses,
                    property_ownership, dependents, risk_level, default_probability,
                    repayment_probability, recommendation, badge, model_used, prediction_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', seed_records)
            conn.commit()
        conn.close()

def db_save_prediction(d):
    """Saves a prediction record to SQLite or MongoDB."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        doc = d.copy()
        doc['prediction_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result = predictions_col.insert_one(doc)
        return str(result.inserted_id)
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (
                applicant_name, age, gender, annual_income, employment_status,
                years_employment, education, marital_status, loan_amount, loan_purpose,
                interest_rate, loan_term, credit_score, dti, existing_loans,
                credit_cards, previous_defaults, savings_balance, monthly_expenses,
                property_ownership, dependents, risk_level, default_probability,
                repayment_probability, recommendation, badge, model_used
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            d['applicant_name'], d['age'], d['gender'], d['annual_income'], d['employment_status'],
            d['years_employment'], d['education'], d['marital_status'], d['loan_amount'], d['loan_purpose'],
            d['interest_rate'], d['loan_term'], d['credit_score'], d['dti'], d['existing_loans'],
            d['credit_cards'], d['previous_defaults'], d['savings_balance'], d['monthly_expenses'],
            d['property_ownership'], d['dependents'], d['risk_level'], d['default_probability'],
            d['repayment_probability'], d['recommendation'], d['badge'], d['model_used']
        ))
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id

def db_get_predictions(search='', risk='', sort_by='prediction_date', order='DESC', limit=10, offset=0, fetch_all=False):
    """Retrieves paginated search predictions."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        query = {}
        if search:
            query['applicant_name'] = {'$regex': search, '$options': 'i'}
        if risk:
            query['risk_level'] = risk
            
        sort_dir = -1 if order == 'DESC' else 1
        mongo_sort = [(sort_by, sort_dir)]
        
        cursor = predictions_col.find(query).sort(mongo_sort)
        total_records = predictions_col.count_documents(query)
        
        if not fetch_all:
            cursor = cursor.skip(offset).limit(limit)
            
        rows = []
        for doc in cursor:
            row = dict(doc)
            row['id'] = str(row['_id'])
            row['_id'] = str(row['_id'])
            rows.append(row)
            
        return rows, total_records
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        query = "SELECT * FROM predictions WHERE 1=1"
        params = []
        if search:
            query += " AND applicant_name LIKE ?"
            params.append(f"%{search}%")
        if risk:
            query += " AND risk_level = ?"
            params.append(risk)
            
        query += f" ORDER BY {sort_by} {order}"
        
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()[0]
        
        if not fetch_all:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
        cursor.execute(query, params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows, total_records

def db_delete_prediction(pred_id):
    """Deletes record by ID."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        predictions_col.delete_one({'_id': ObjectId(pred_id)})
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = ?", (int(pred_id),))
        conn.commit()
        conn.close()

def db_get_details(pred_id):
    """Fetches details of a prediction."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        doc = predictions_col.find_one({'_id': ObjectId(pred_id)})
        if doc:
            row = dict(doc)
            row['id'] = str(row['_id'])
            row['_id'] = str(row['_id'])
            return row
        return None
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE id = ?", (int(pred_id),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

def db_get_unique_customers():
    """Aggregates unique profiles list."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        pipeline = [
            {"$sort": {"prediction_date": 1}},
            {"$group": {
                "_id": "$applicant_name",
                "max_score": {"$max": "$credit_score"},
                "last_date": {"$last": "$prediction_date"},
                "total_loans": {"$sum": 1},
                "risk": {"$last": "$risk_level"},
                "badge": {"$last": "$badge"},
                "income": {"$last": "$annual_income"}
            }},
            {"$sort": {"last_date": -1}}
        ]
        cursor = predictions_col.aggregate(pipeline)
        rows = []
        for doc in cursor:
            rows.append({
                'applicant_name': doc['_id'],
                'max_score': doc['max_score'],
                'last_date': doc['last_date'],
                'total_loans': doc['total_loans'],
                'risk': doc['risk'],
                'badge': doc['badge'],
                'income': doc['income']
            })
        return rows
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT applicant_name, 
                   MAX(credit_score) as max_score, 
                   MAX(prediction_date) as last_date, 
                   COUNT(*) as total_loans, 
                   MAX(risk_level) as risk,
                   MAX(badge) as badge,
                   MAX(annual_income) as income
            FROM predictions 
            GROUP BY applicant_name 
            ORDER BY last_date DESC
        """)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

def db_get_customer_history(name):
    """Retrieves historical logs list for timeline graphs."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        cursor = predictions_col.find({'applicant_name': name}).sort('prediction_date', 1)
        rows = []
        for doc in cursor:
            row = dict(doc)
            row['id'] = str(row['_id'])
            row['_id'] = str(row['_id'])
            rows.append(row)
        return rows
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions WHERE applicant_name = ? ORDER BY prediction_date ASC", (name,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

def db_get_dashboard_stats():
    """Aggregates dashboard counts, DTI levels, monthly volumes."""
    if DB_ENGINE == 'mongodb':
        predictions_col = mongo_db['predictions']
        total = predictions_col.count_documents({})
        if total == 0:
            return 0, 0, 0, 0, 0.0, 0.0, 0.0, {}, {}, {}, [], {}
            
        # Approved/Rejected Counts
        approved = predictions_col.count_documents({'risk_level': 'Low Risk'})
        medium = predictions_col.count_documents({'risk_level': 'Medium Risk'})
        rejected = predictions_col.count_documents({'risk_level': 'High Risk'})
        
        # Averages
        pipeline_avg = [
            {"$group": {
                "_id": None,
                "avg_score": {"$avg": "$credit_score"},
                "avg_income": {"$avg": "$annual_income"},
                "avg_loan": {"$avg": "$loan_amount"}
            }}
        ]
        avgs = list(predictions_col.aggregate(pipeline_avg))
        avg_score = round(avgs[0]['avg_score'] or 0, 1) if avgs else 0
        avg_income = round(avgs[0]['avg_income'] or 0, 0) if avgs else 0
        avg_loan = round(avgs[0]['avg_loan'] or 0, 0) if avgs else 0
        
        # Default Rate: (Rejected + 0.3 * Medium) / Total
        default_rate = round(((rejected + 0.3 * medium) / total) * 100, 1)
        
        # Monthly Stats
        pipeline_month = [
            {"$project": {"month": {"$substr": ["$prediction_date", 0, 7]}}},
            {"$group": {"_id": "$month", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        monthly_stats = {doc['_id']: doc['count'] for doc in predictions_col.aggregate(pipeline_month)}
        
        # Purpose distribution
        pipeline_purpose = [
            {"$group": {"_id": "$loan_purpose", "count": {"$sum": 1}}}
        ]
        purpose_stats = {doc['_id']: doc['count'] for doc in predictions_col.aggregate(pipeline_purpose)}
        
        # Employment distribution
        pipeline_emp = [
            {"$group": {"_id": "$employment_status", "count": {"$sum": 1}}}
        ]
        employment_stats = {doc['_id']: doc['count'] for doc in predictions_col.aggregate(pipeline_emp)}
        
        # Scatter list
        cursor_scatter = predictions_col.find({}, {'annual_income': 1, 'loan_amount': 1, 'risk_level': 1})
        scatter_data = [{'income': doc['annual_income'], 'loan': doc['loan_amount'], 'risk': doc['risk_level']} for doc in cursor_scatter]
        
        # Score Ranges
        score_ranges = {"300-579": 0, "580-669": 0, "670-739": 0, "740-799": 0, "800-850": 0}
        cursor_scores = predictions_col.find({}, {'credit_score': 1})
        for doc in cursor_scores:
            s = doc['credit_score']
            if s < 580: score_ranges["300-579"] += 1
            elif s < 670: score_ranges["580-669"] += 1
            elif s < 740: score_ranges["670-739"] += 1
            elif s < 800: score_ranges["740-799"] += 1
            else: score_ranges["800-850"] += 1
            
        # Recent Predictions
        cursor_recent = predictions_col.find().sort('prediction_date', -1).limit(5)
        recent = []
        for doc in cursor_recent:
            row = dict(doc)
            row['id'] = str(row['_id'])
            row['_id'] = str(row['_id'])
            recent.append(row)
            
        # High Risk
        cursor_high = predictions_col.find({'risk_level': 'High Risk'}).sort('prediction_date', -1).limit(4)
        top_high = []
        for doc in cursor_high:
            row = dict(doc)
            row['id'] = str(row['_id'])
            row['_id'] = str(row['_id'])
            top_high.append(row)
            
        return total, approved, rejected, medium, avg_score, default_rate, avg_income, avg_loan, monthly_stats, purpose_stats, employment_stats, scatter_data, score_ranges, recent, top_high
    else:
        # SQLite Fallback
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*), AVG(credit_score), AVG(annual_income), AVG(loan_amount) FROM predictions")
        stats = cursor.fetchone()
        total = stats[0] or 0
        avg_score = round(stats[1] or 0, 1)
        avg_income = round(stats[2] or 0, 0)
        avg_loan = round(stats[3] or 0, 0)
        
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'Low Risk'")
        approved = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'Medium Risk'")
        medium = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'High Risk'")
        rejected = cursor.fetchone()[0] or 0
        
        default_rate = 0.0
        if total > 0:
            default_rate = round(((rejected + 0.3 * medium) / total) * 100, 1)
            
        # Monthly Stats
        cursor.execute("""
            SELECT strftime('%Y-%m', prediction_date) as month, COUNT(*) as count 
            FROM predictions 
            GROUP BY month 
            ORDER BY month ASC
        """)
        monthly_stats = {row['month']: row['count'] for row in cursor.fetchall()}
        
        # Purpose stats
        cursor.execute("SELECT loan_purpose, COUNT(*) FROM predictions GROUP BY loan_purpose")
        purpose_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Employment stats
        cursor.execute("SELECT employment_status, COUNT(*) FROM predictions GROUP BY employment_status")
        employment_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Scatter list
        cursor.execute("SELECT annual_income, loan_amount, risk_level FROM predictions")
        scatter_data = [{'income': row['annual_income'], 'loan': row['loan_amount'], 'risk': row['risk_level']} for row in cursor.fetchall()]
        
        # Score Ranges
        cursor.execute("SELECT credit_score FROM predictions WHERE credit_score IS NOT NULL")
        score_ranges = {"300-579": 0, "580-669": 0, "670-739": 0, "740-799": 0, "800-850": 0}
        for row in cursor.fetchall():
            s = row[0]
            if s < 580: score_ranges["300-579"] += 1
            elif s < 670: score_ranges["580-669"] += 1
            elif s < 740: score_ranges["670-739"] += 1
            elif s < 800: score_ranges["740-799"] += 1
            else: score_ranges["800-850"] += 1
            
        # Recent List
        cursor.execute("SELECT * FROM predictions ORDER BY prediction_date DESC LIMIT 5")
        recent = [dict(row) for row in cursor.fetchall()]
        
        # High Risk
        cursor.execute("SELECT * FROM predictions WHERE risk_level = 'High Risk' ORDER BY prediction_date DESC LIMIT 4")
        top_high = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return total, approved, rejected, medium, avg_score, default_rate, avg_income, avg_loan, monthly_stats, purpose_stats, employment_stats, scatter_data, score_ranges, recent, top_high

def db_get_engine_info():
    """Returns database metadata statistics."""
    if DB_ENGINE == 'mongodb':
        try:
            mongo_client.server_info()
            status = 'CONNECTED (MongoDB Active)'
        except:
            status = 'DISCONNECTED (Falling back to SQLite)'
    else:
        status = 'CONNECTED (SQLite Active)'
    return DB_ENGINE.upper(), status

def db_log_action(username, role, action, details):
    """Saves an administrative audit log entry to SQLite or MongoDB."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if DB_ENGINE == 'mongodb':
        logs_col = mongo_db['audit_logs']
        logs_col.insert_one({
            'username': username or 'Anonymous',
            'role': role or 'Viewer',
            'action': action,
            'details': details,
            'timestamp': timestamp
        })
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                role TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            INSERT INTO audit_logs (username, role, action, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (username or 'Anonymous', role or 'Viewer', action, details, timestamp))
        conn.commit()
        conn.close()

def db_get_audit_logs(limit=50):
    """Retrieves all recent audit logs."""
    if DB_ENGINE == 'mongodb':
        logs_col = mongo_db['audit_logs']
        cursor = logs_col.find().sort('timestamp', -1).limit(limit)
        rows = []
        for doc in cursor:
            row = dict(doc)
            row['id'] = str(row['_id'])
            del row['_id']
            rows.append(row)
        return rows
    else:
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                role TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
