import os
import numpy as np
import pandas as pd

def generate_credit_dataset(num_samples=2500, random_seed=42):
    np.random.seed(random_seed)
    
    # 1. Age (18 to 75)
    age = np.random.randint(18, 76, size=num_samples)
    
    # 2. Gender
    gender_choices = ['Male', 'Female', 'Non-Binary']
    gender = np.random.choice(gender_choices, size=num_samples, p=[0.48, 0.48, 0.04])
    
    # 3. Education
    edu_choices = ['High School', 'Associate', 'Bachelor', 'Master', 'Doctorate']
    education = np.random.choice(edu_choices, size=num_samples, p=[0.25, 0.15, 0.40, 0.15, 0.05])
    
    # 4. Marital Status
    marital_choices = ['Single', 'Married', 'Divorced', 'Widowed']
    marital_status = np.random.choice(marital_choices, size=num_samples, p=[0.35, 0.45, 0.15, 0.05])
    
    # 5. Employment Status
    emp_choices = ['Employed', 'Self-Employed', 'Retired', 'Unemployed']
    employment_status = []
    for a in age:
        if a < 22:
            # Young, higher likelihood of unemployed or student-age
            p = [0.40, 0.10, 0.00, 0.50]
        elif a > 65:
            # Retirement age
            p = [0.05, 0.05, 0.85, 0.05]
        else:
            p = [0.75, 0.15, 0.02, 0.08]
        employment_status.append(np.random.choice(emp_choices, p=p))
    employment_status = np.array(employment_status)
    
    # 6. Years of Employment
    years_employment = []
    for i in range(num_samples):
        emp_s = employment_status[i]
        a = age[i]
        if emp_s == 'Unemployed':
            years_employment.append(0.0)
        elif emp_s == 'Retired':
            # Worked for a long time
            max_work = min(45, a - 18)
            if max_work <= 15:
                years_employment.append(float(np.random.randint(0, max(1, max_work + 1))))
            else:
                years_employment.append(float(np.random.randint(15, max_work)))
        else:
            max_work = min(45, a - 18)
            if max_work <= 0:
                years_employment.append(0.0)
            else:
                years_employment.append(round(np.random.uniform(0.5, max_work), 1))
    years_employment = np.array(years_employment)
    
    # 7. Annual Income ($15,000 to $250,000)
    # Correlate slightly with age and education
    annual_income = []
    for i in range(num_samples):
        edu = education[i]
        a = age[i]
        emp_s = employment_status[i]
        
        # Base income range depending on education
        if edu == 'High School':
            base = np.random.uniform(15000, 50000)
        elif edu == 'Associate':
            base = np.random.uniform(25000, 70000)
        elif edu == 'Bachelor':
            base = np.random.uniform(40000, 120000)
        elif edu == 'Master':
            base = np.random.uniform(55000, 170000)
        else: # Doctorate
            base = np.random.uniform(70000, 250000)
            
        # Age multiplier (peak earnings at 40-55)
        age_factor = 1.0 + (0.5 * (1.0 - abs(a - 48)/30)) if a >= 18 and a <= 78 else 1.0
        income = base * max(0.5, age_factor)
        
        # Employment modifier
        if emp_s == 'Unemployed':
            income = np.random.uniform(5000, 15000) # minimal income (benefits/informal)
        elif emp_s == 'Retired':
            income = income * 0.4 # pension is lower
            
        annual_income.append(round(income, -2))
    annual_income = np.array(annual_income)
    
    # 8. Monthly Income
    monthly_income = np.round(annual_income / 12, 2)
    
    # 9. Dependents (0 to 4)
    dependents = []
    for a in age:
        if a < 25 or a > 55:
            p = [0.80, 0.15, 0.05, 0.00, 0.00]
        else:
            p = [0.30, 0.30, 0.25, 0.10, 0.05]
        dependents.append(np.random.choice([0, 1, 2, 3, 4], p=p))
    dependents = np.array(dependents)
    
    # 10. Monthly Expenses
    monthly_expenses = []
    for i in range(num_samples):
        inc = monthly_income[i]
        deps = dependents[i]
        # Basic living expense + proportional to income + dependents cost
        base_exp = np.random.uniform(400, 1200)
        prop_exp = inc * np.random.uniform(0.20, 0.45)
        dep_exp = deps * np.random.uniform(150, 400)
        total_exp = base_exp + prop_exp + dep_exp
        
        # Constraint: Expenses shouldn't easily exceed monthly income unless low income
        if total_exp > inc * 0.9 and inc > 1500:
            total_exp = inc * np.random.uniform(0.70, 0.85)
        monthly_expenses.append(round(total_exp, 2))
    monthly_expenses = np.array(monthly_expenses)
    
    # 11. Credit Score (300 to 850)
    # Correlated with age, income, and randomly
    credit_score = []
    for i in range(num_samples):
        a = age[i]
        inc = annual_income[i]
        emp_s = employment_status[i]
        
        # Base credit score
        base = 580 + (a - 18) * 2.0 # older people have longer history
        base += (inc / 50000) * 15 # higher income helps
        
        if emp_s == 'Unemployed':
            base -= 50
            
        noise = np.random.normal(0, 70)
        score = int(np.clip(base + noise, 300, 850))
        credit_score.append(score)
    credit_score = np.array(credit_score)
    
    # 12. Savings Balance
    savings_balance = []
    for i in range(num_samples):
        inc = annual_income[i]
        score = credit_score[i]
        
        # Savings are highly correlated with income and credit score (discipline)
        save_ratio = np.random.exponential(scale=0.15) # most have small ratios, few have large
        if score > 750:
            save_ratio += np.random.uniform(0.05, 0.35)
        elif score < 550:
            save_ratio *= 0.3
            
        savings = inc * save_ratio
        savings_balance.append(round(savings, -2))
    savings_balance = np.array(savings_balance)
    
    # 13. Loan Amount
    loan_amount = []
    for i in range(num_samples):
        inc = annual_income[i]
        score = credit_score[i]
        
        # Loan size requested depends on income
        max_loan = inc * np.random.uniform(0.1, 0.6)
        # Cap absolute loan sizes
        max_loan = min(150000, max_loan)
        
        loan = np.random.uniform(2000, max(5000, max_loan))
        
        # People with good credit score can secure larger loans
        if score < 500:
            loan *= 0.6
            
        loan_amount.append(round(loan, -2))
    loan_amount = np.array(loan_amount)
    
    # 14. Loan Purpose
    purposes = ['Debt Consolidation', 'Home Improvement', 'Education', 'Auto', 'Business', 'Personal']
    loan_purpose = np.random.choice(purposes, size=num_samples, p=[0.35, 0.20, 0.15, 0.12, 0.10, 0.08])
    
    # 15. Loan Term (12, 24, 36, 60)
    loan_term = np.random.choice([12, 24, 36, 60], size=num_samples, p=[0.15, 0.25, 0.40, 0.20])
    
    # 16. Interest Rate (3.5% to 25.0%)
    # Highly correlated with credit score (risk-based pricing)
    interest_rate = []
    for i in range(num_samples):
        score = credit_score[i]
        term = loan_term[i]
        
        # Base rate
        if score > 800:
            rate = np.random.uniform(3.5, 6.5)
        elif score > 740:
            rate = np.random.uniform(6.0, 9.5)
        elif score > 670:
            rate = np.random.uniform(9.0, 13.5)
        elif score > 580:
            rate = np.random.uniform(13.0, 18.5)
        else:
            rate = np.random.uniform(18.0, 25.0)
            
        # Longer term -> slightly higher rate
        if term == 60:
            rate += np.random.uniform(0.5, 2.0)
            
        interest_rate.append(round(rate, 2))
    interest_rate = np.array(interest_rate)
    
    # 17. Number of Existing Loans (0 to 5)
    existing_loans = []
    for score in credit_score:
        if score > 700:
            p = [0.35, 0.40, 0.18, 0.05, 0.01, 0.01]
        elif score < 500:
            p = [0.60, 0.25, 0.10, 0.03, 0.01, 0.01]
        else:
            p = [0.45, 0.35, 0.13, 0.05, 0.01, 0.01]
        existing_loans.append(np.random.choice([0, 1, 2, 3, 4, 5], p=p))
    existing_loans = np.array(existing_loans)
    
    # 18. Number of Credit Cards (0 to 10)
    credit_cards = []
    for score in credit_score:
        if score > 750:
            base_cards = np.random.randint(3, 11)
        elif score < 500:
            base_cards = np.random.randint(0, 4)
        else:
            base_cards = np.random.randint(1, 8)
        credit_cards.append(base_cards)
    credit_cards = np.array(credit_cards)
    
    # 19. Previous Loan Defaults (0 to 3)
    # Correlated with credit score
    previous_defaults = []
    for score in credit_score:
        if score > 750:
            p = [0.99, 0.01, 0.00, 0.00]
        elif score > 650:
            p = [0.92, 0.06, 0.01, 0.01]
        elif score > 550:
            p = [0.75, 0.18, 0.05, 0.02]
        else:
            p = [0.40, 0.35, 0.15, 0.10]
        previous_defaults.append(np.random.choice([0, 1, 2, 3], p=p))
    previous_defaults = np.array(previous_defaults)
    
    # 20. Debt-to-Income (DTI) Ratio (0.05 to 0.70)
    # Monthly Debts (existing loan payments + credit cards) / Monthly Income
    dti = []
    for i in range(num_samples):
        inc = monthly_income[i]
        cards = credit_cards[i]
        loans = existing_loans[i]
        
        # Calculate approximate monthly debt payments
        estimated_debt = loans * np.random.uniform(150, 400) + cards * np.random.uniform(20, 70)
        ratio = estimated_debt / inc if inc > 0 else 0.50
        ratio += np.random.uniform(0.02, 0.10)
        
        dti.append(round(np.clip(ratio, 0.05, 0.70), 2))
    dti = np.array(dti)
    
    # 21. Property Ownership
    prop_choices = ['Own', 'Mortgage', 'Rent']
    property_ownership = []
    for i in range(num_samples):
        a = age[i]
        inc = annual_income[i]
        if a < 26:
            p = [0.05, 0.15, 0.80]
        elif inc > 100000:
            p = [0.40, 0.50, 0.10]
        else:
            p = [0.15, 0.45, 0.40]
        property_ownership.append(np.random.choice(prop_choices, p=p))
    property_ownership = np.array(property_ownership)
    
    # ----------------------------------------------------
    # Calculate Risk Score and Target Class
    # ----------------------------------------------------
    risk_score = np.zeros(num_samples)
    
    for i in range(num_samples):
        score = 50.0
        
        # 1. Credit Score impact
        cs = credit_score[i]
        if cs < 580:
            score += 26.0
        elif cs < 670:
            score += 13.0
        elif cs >= 740 and cs < 800:
            score -= 13.0
        elif cs >= 800:
            score -= 26.0
            
        # 2. DTI impact
        ratio = dti[i]
        if ratio > 0.50:
            score += 16.0
        elif ratio > 0.35:
            score += 8.0
        elif ratio < 0.20:
            score -= 8.0
            
        # 3. Previous Defaults impact
        defaults = previous_defaults[i]
        if defaults >= 2:
            score += 28.0
        elif defaults == 1:
            score += 14.0
        else:
            score -= 5.0
            
        # 4. Savings Balance relative to Loan Amount
        savings = savings_balance[i]
        loan = loan_amount[i]
        if savings > loan:
            score -= 15.0
        elif savings < 0.10 * loan:
            score += 10.0
            
        # 5. Employment Status
        emp = employment_status[i]
        if emp == 'Unemployed':
            score += 20.0
        elif emp == 'Self-Employed':
            score += 5.0
        elif emp == 'Employed':
            score -= 5.0
            
        # 6. Property Ownership
        prop = property_ownership[i]
        if prop == 'Rent':
            score += 5.0
        elif prop == 'Own':
            score -= 5.0
            
        # Add normal noise
        score += np.random.normal(0, 4.5)
        risk_score[i] = np.clip(score, 0, 100)
        
    # Categorize Risk
    risk_level = []
    for rs in risk_score:
        if rs < 36:
            risk_level.append('Low Risk')
        elif rs < 62:
            risk_level.append('Medium Risk')
        else:
            risk_level.append('High Risk')
            
    # Create DataFrame
    df = pd.DataFrame({
        'Age': age,
        'Gender': gender,
        'Annual Income': annual_income,
        'Monthly Income': monthly_income,
        'Employment Status': employment_status,
        'Years of Employment': years_employment,
        'Education': education,
        'Marital Status': marital_status,
        'Loan Amount': loan_amount,
        'Loan Purpose': loan_purpose,
        'Interest Rate': interest_rate,
        'Loan Term': loan_term,
        'Credit Score': credit_score,
        'Debt-to-Income Ratio': dti,
        'Number of Existing Loans': existing_loans,
        'Number of Credit Cards': credit_cards,
        'Previous Loan Defaults': previous_defaults,
        'Savings Balance': savings_balance,
        'Monthly Expenses': monthly_expenses,
        'Property Ownership': property_ownership,
        'Dependents': dependents,
        'Risk Level': risk_level
    })
    
    # Introduce some synthetic missing values to show cleaning
    # Credit Score: 2% missing
    mask = np.random.rand(num_samples) < 0.02
    df.loc[mask, 'Credit Score'] = np.nan
    
    # Years of Employment: 2% missing
    mask = np.random.rand(num_samples) < 0.02
    df.loc[mask, 'Years of Employment'] = np.nan
    
    # Savings Balance: 3% missing
    mask = np.random.rand(num_samples) < 0.03
    df.loc[mask, 'Savings Balance'] = np.nan
    
    # Debt-to-Income Ratio: 1% missing
    mask = np.random.rand(num_samples) < 0.01
    df.loc[mask, 'Debt-to-Income Ratio'] = np.nan
    
    # Introduce a few duplicate rows (say 15 rows)
    dup_indices = np.random.choice(df.index, size=15, replace=False)
    duplicates = df.loc[dup_indices].copy()
    df = pd.concat([df, duplicates], ignore_index=True)
    
    # Shuffle
    df = df.sample(frac=1, random_state=random_seed).reset_index(drop=True)
    return df

if __name__ == '__main__':
    os.makedirs('dataset', exist_ok=True)
    df = generate_credit_dataset()
    df.to_csv('dataset/credit_risk_dataset.csv', index=False)
    print(f"Generated synthetic dataset with {df.shape[0]} rows and {df.shape[1]} columns.")
    print(f"Data saved to dataset/credit_risk_dataset.csv")
    print("\nRisk Level Distribution:")
    print(df['Risk Level'].value_counts(dropna=False))
