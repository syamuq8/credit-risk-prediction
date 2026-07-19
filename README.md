# Credit Risk Prediction System

An AI-powered banking-style web application designed to evaluate loan applicant default risks. The system leverages multiple machine learning models (Logistic Regression, Decision Trees, Random Forests, Support Vector Machines, XGBoost, and Gradient Boosting) to classify applicants into **Low Risk**, **Medium Risk**, or **High Risk** categories. It also provides predictions, decision confidence, Explainable AI (XAI) feature contributions, and custom credit-optimization suggestions.

---

## 🚀 Key Features

- **Model Comparison Dashboard**: Renders aggregate metrics (approved/rejected ratios, default rates, FICO distributions) with interactive Chart.js widgets.
- **Explainable AI (XAI)**: Identifies specific features (e.g., low FICO, high DTI) driving a risk decision and plots their impact using custom feature contribution bar graphs.
- **Autofill Scenario Profiles**: Includes pre-configured profiles (Low Risk, Medium Risk, High Risk) to allow instant testing and verification.
- **Interactive Predictive History Log**: Saves and aggregates every assessment in an SQLite database, supporting custom customer searches, risk filters, and raw CSV exports.
- **Jupyter Notebooks Included**: Fully implemented EDA and model training notebooks are included for educational transparency.

---

## 📁 Project Structure

```
credit-risk-prediction/
│
├── dataset/
│   └── credit_risk_dataset.csv     # Synthetic credit risk dataset (~2,500 samples)
├── notebooks/
│   ├── EDA.ipynb                    # Exploratory Data Analysis notebook
│   └── ModelTraining.ipynb         # Machine Learning pipeline notebook
├── models/
│   ├── credit_model.pkl            # Serialized best model (Gradient Boosting)
│   ├── scaler.pkl                  # Serialized StandardScaler
│   ├── encoder.pkl                 # Serialized OneHotEncoder
│   ├── preprocessor.pkl            # Preprocessor dictionary metadata
│   └── model_comparison.json       # JSON data of all model metrics
├── static/
│   ├── css/
│   │   └── style.css               # Modern glassmorphism theme and styling
│   ├── js/
│   │   ├── main.js                 # Form autofill and print utility functions
│   │   └── charts.js               # Chart.js initialization routines
│   └── images/
│       ├── roc_curve.png           # Pipeline evaluation ROC curves
│       ├── confusion_matrix.png    # Pipeline evaluation Confusion matrix heatmap
│       └── feature_importance.png  # Pipeline evaluation top-10 importances
├── templates/
│   ├── base.html                   # HTML base template structure
│   ├── dashboard.html              # Analytics dashboard layout
│   ├── predict.html                # New assessment entry form
│   ├── result.html                 # Applicant risk assessment report
│   ├── history.html                # SQLite database log search table
│   └── model_info.html             # Model metrics and pipeline plots
├── app.py                          # Flask application backend
├── predict.py                      # Model inference & explainability engine
├── train_model.py                  # ML pipeline trainer
├── generate_data.py                # Synthetic dataset generator
├── requirements.txt                # Python library dependencies
└── README.md                       # Documentation file
```

---

## 📊 Dataset Description

The system operates on 21 applicant features:
1. **Age**: Applicant age (18 to 75).
2. **Gender**: Male, Female, Non-Binary.
3. **Annual Income**: Yearly earnings.
4. **Monthly Income**: Calculated as `Annual Income / 12`.
5. **Employment Status**: Employed, Self-Employed, Retired, Unemployed.
6. **Years of Employment**: Years active at current job.
7. **Education**: High School, Associate, Bachelor, Master, Doctorate.
8. **Marital Status**: Single, Married, Divorced, Widowed.
9. **Loan Amount**: Requested borrowing.
10. **Loan Purpose**: Auto, Business, Debt Consolidation, Education, Home Improvement, Personal.
11. **Interest Rate**: Risk-adjusted interest charges (3.5% to 25.0%).
12. **Loan Term**: Duration of the loan (12, 24, 36, or 60 months).
13. **Credit Score**: FICO range (300 to 850).
14. **Debt-to-Income (DTI) Ratio**: Total monthly debts divided by monthly income.
15. **Number of Existing Loans**: Quantity of current open loans.
16. **Number of Credit Cards**: Quantity of open cards.
17. **Previous Loan Defaults**: History of defaulting (0 to 3).
18. **Savings Balance**: Financial asset reserves.
19. **Monthly Expenses**: Base living costs.
20. **Property Ownership**: Own, Mortgage, Rent.
21. **Dependents**: Number of household dependents (0 to 4).

---

## 🛠️ Data Preprocessing & Pipeline

1. **Duplicate Removal**: Identifies and drops identical records.
2. **Missing Values**: Imputes numerical features with the training set **median** and categorical features with the **mode**.
3. **Outliers Capping**: Caps numerical outliers at the 1st and 99th percentiles (Winsorization) to improve linear models.
4. **Encoding**: One-Hot Encodes categorical features with `handle_unknown='ignore'`.
5. **Scaling**: Scales numerical inputs using standard scaling (`StandardScaler`).

---

## 📈 Model Comparison & Evaluation

Six classifiers were trained and compared. The test results are detailed below:

| Model Name | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Gradient Boosting** | **85.8%** | **0.859** | **0.858** | **0.858** | **0.954** |
| **Logistic Regression** | 84.2% | 0.841 | 0.842 | 0.842 | 0.952 |
| **XGBoost** | 83.6% | 0.836 | 0.836 | 0.836 | 0.952 |
| **Random Forest** | 83.0% | 0.835 | 0.830 | 0.831 | 0.940 |
| **Support Vector Machine**| 82.4% | 0.826 | 0.824 | 0.825 | 0.945 |
| **Decision Tree** | 74.6% | 0.759 | 0.746 | 0.749 | 0.869 |

**Gradient Boosting Classifier** was selected as the default estimator due to its superior F1-Score (0.858) and ROC-AUC (0.954).

---

## 🛠️ Technologies Used

- **Backend**: Python 3.11, Flask
- **Machine Learning**: Scikit-learn, Pandas, NumPy, Joblib, XGBoost, SHAP
- **Frontend & UI**: HTML5, Vanilla CSS, JS, Bootstrap 5, Bootstrap Icons, Chart.js
- **Database**: SQLite (local portability) & MongoDB / PyMongo (cloud scalability)
- **Production Server**: Gunicorn

---

## ⚙️ Installation Guide

### Prerequisites
- Python 3.10 or higher installed.

### Setup Steps
1. **Clone or copy** the project files to a local directory:
   `C:\Users\pisin\.gemini\antigravity\scratch\credit-risk-prediction`

2. **Open a terminal** in the folder and install requirements:
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate the Dataset**:
   ```bash
   python generate_data.py
   ```

4. **Train the ML Models**:
   ```bash
   python train_model.py
   ```

5. **Start the Flask Application**:
   ```bash
   python app.py
   ```

6. **Access the App**:
   Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🐙 GitHub Repository Setup

To push your local repository to GitHub:

1. **Initialize Git**:
   ```bash
   git init
   ```
2. **Add Files**:
   ```bash
   git add .
   ```
3. **Commit**:
   ```bash
   git commit -m "Initial commit: credit risk prediction system"
   ```
4. **Create Repository on GitHub**:
   Create a new blank repository on your GitHub account.
5. **Link and Push**:
   ```bash
   git remote add origin https://github.com/your-username/your-repo-name.git
   git branch -M main
   git push -u origin main
   ```

---

## 🌐 Production Deployment Guide

This system is deployment-ready for cloud hosting platforms such as **Render** or **Railway**.

### Platform Configuration Settings

Configure the following settings in your platform dashboard:

1. **Environment Runtime**: Python (version `3.11.9` specified in [runtime.txt](file:///C:/Users/pisin/.gemini/antigravity/scratch/credit-risk-prediction/runtime.txt))
2. **Build Command**:
   ```bash
   pip install -r requirements.txt && python generate_data.py && python train_model.py
   ```
3. **Start Command**:
   ```bash
   gunicorn app:app
   ```
4. **Environment Variables**:
   Add the following variables in your dashboard settings:
   - `FLASK_SECRET_KEY`: A secure random key to sign active sessions.
   - `DB_ENGINE`: `sqlite` or `mongodb` depending on your selected storage engine.
   - `MONGO_URI`: Connection string pointing to your Atlas MongoDB clusters (e.g., `mongodb+srv://...` if using MongoDB).

---

## ⚡ Vercel Deployment Guide

This project is fully optimized for serverless deployments on **Vercel** (with no credit card verification required).

### Vercel Configuration Details
- A [vercel.json](file:///C:/Users/pisin/.gemini/antigravity/scratch/credit-risk-prediction/vercel.json) file has been configured in the root directory to route serverless requests to the Flask instance.
- Filesystem write processes are automatically redirected to the Vercel-compatible `/tmp` directory at runtime to prevent permission crashes.

### Deployment Steps
1. **Install Vercel CLI** (requires Node.js):
   ```bash
   npm install -g vercel
   ```
2. **Deploy & Link**: Run the following command inside the project directory:
   ```bash
   vercel
   ```
   Follow the prompts to log in and set up your project.
3. **Configure Environment Variables**:
   In your Vercel project settings dashboard, add:
   - `FLASK_SECRET_KEY`: A secure random secret key.
   - `DB_ENGINE`: `sqlite` (or `mongodb` to connect to a free MongoDB Atlas cloud cluster for permanent data persistence).
4. **Deploy Live**:
   ```bash
   vercel --prod
   ```

---

## ☁️ Koyeb Deployment Guide

This project is fully ready for containerized deployment on **Koyeb**'s free tier.

### Deployment Steps
1. Go to **[Koyeb Dashboard](https://app.koyeb.com)** and sign in.
2. Click **Create Service**.
3. Select **GitHub** as the deployment source and choose your `credit-risk-prediction` repository.
4. Configure the service settings:
   - **Builder**: Select `Buildpack` (automatic detection).
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt && python generate_data.py && python train_model.py
     ```
   - **Run Command**: 
     ```bash
     gunicorn app:app
     ```
5. Add the following **Environment Variables**:
   - `FLASK_SECRET_KEY`: A secure random secret key.
   - `DB_ENGINE`: `sqlite` (or `mongodb` for permanent persistence).
   - `MONGO_URI`: MongoDB Atlas connection string (if using MongoDB).
6. Choose the **Free Nano Instance** and click **Deploy**.

---

## 🚂 Railway Deployment Guide

This project is fully ready for containerized deployment on **Railway**.

### Deployment Steps
1. Go to **[Railway Dashboard](https://railway.app)** and log in using GitHub.
2. Click **+ New Project** and select **Deploy from GitHub repo**.
3. Choose your `credit-risk-prediction` repository.
4. Click **Deploy Now**.
5. Once created, go to the **Settings** tab of the service:
   - Under **Build Command**, input:
     ```bash
     pip install -r requirements.txt && python generate_data.py && python train_model.py
     ```
   - Under **Start Command**, verify it uses:
     ```bash
     gunicorn app:app
     ```
6. Go to the **Variables** tab and click **Add Variable**:
   - `FLASK_SECRET_KEY`: A secure random secret key.
   - `DB_ENGINE`: `sqlite` (or `mongodb` for permanent persistence).
   - `MONGO_URI`: MongoDB Atlas connection string (if using MongoDB).
7. Under the **Settings** tab in the **Networking** section, click **Generate Domain** to get your public HTTPS URL.

---

## 📸 Screenshots
*(Place screen captures here to showcase the beautiful Harlequin Green glassmorphism design and interactive timelines)*
- **Dashboard**: `![Dashboard Layout](static/images/screenshot_dashboard.png)`
- **Simulator**: `![Risk Simulator](static/images/screenshot_simulator.png)`

---

## 📄 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🔮 Future Improvements

- **Interactive SHAP Plots**: Integrate SHAP JS visualization libraries to create interactive force plots in the browser.
- **Deep Learning Model**: Introduce an artificial neural network (ANN) via PyTorch/TensorFlow to evaluate deep learning performance on large-scale datasets.
- **Real-time API Access**: Add token-based authentication (OAuth2) to allow external banking platforms to run assessments programmatically.
- **Dynamic Interest Rates**: Implement regression estimators to automatically suggest optimal loan interest rates based on calculated default risk.
