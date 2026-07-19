import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, roc_curve, auc
)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

# Force matplotlib to use 'Agg' backend
import matplotlib
matplotlib.use('Agg')

def train_and_evaluate():
    print("Starting Comprehensive ML Pipeline...")
    
    os.makedirs('models', exist_ok=True)
    os.makedirs(os.path.join('static', 'images'), exist_ok=True)
    
    data_path = 'dataset/credit_risk_dataset.csv'
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Dataset not found at {data_path}. Please run generate_data.py first.")
        
    df = pd.read_csv(data_path)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
    
    # Generate and save dataset statistics JSON for administrative panels
    missing_report = df.isnull().sum().to_dict()
    num_cols_for_stats = df.select_dtypes(include=[np.number]).columns.tolist()
    correlation_matrix = df[num_cols_for_stats].corr().round(3).to_dict()
    
    dataset_stats = {
        'total_rows': int(df.shape[0]),
        'total_cols': int(df.shape[1]),
        'missing_values': missing_report,
        'correlation': correlation_matrix,
        'summary': df.describe().round(2).to_dict()
    }
    with open('models/dataset_stats.json', 'w') as f:
        import json
        json.dump(dataset_stats, f, indent=4)
    print("Dataset stats successfully saved to models/dataset_stats.json.")
    
    # 2. Remove duplicates
    duplicate_count = df.duplicated().sum()
    if duplicate_count > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        print(f"Removed {duplicate_count} duplicate rows.")
        
    X = df.drop(columns=['Risk Level'])
    y = df['Risk Level']
    
    target_mapping = {'Low Risk': 0, 'Medium Risk': 1, 'High Risk': 2}
    y_encoded = y.map(target_mapping)
    
    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = X.select_dtypes(include=[object]).columns.tolist()
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    num_imputer = SimpleImputer(strategy='median')
    cat_imputer = SimpleImputer(strategy='most_frequent')
    
    X_train_num = pd.DataFrame(num_imputer.fit_transform(X_train[num_cols]), columns=num_cols, index=X_train.index)
    X_test_num = pd.DataFrame(num_imputer.transform(X_test[num_cols]), columns=num_cols, index=X_test.index)
    X_train_cat = pd.DataFrame(cat_imputer.fit_transform(X_train[cat_cols]), columns=cat_cols, index=X_train.index)
    X_test_cat = pd.DataFrame(cat_imputer.transform(X_test[cat_cols]), columns=cat_cols, index=X_test.index)
    
    # Outlier Capping
    for col in num_cols:
        lower_bound = X_train_num[col].quantile(0.01)
        upper_bound = X_train_num[col].quantile(0.99)
        X_train_num[col] = np.clip(X_train_num[col], lower_bound, upper_bound)
        X_test_num[col] = np.clip(X_test_num[col], lower_bound, upper_bound)
        
    # Encode Categorical
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_train_cat_encoded = encoder.fit_transform(X_train_cat)
    X_test_cat_encoded = encoder.transform(X_test_cat)
    
    encoded_cat_names = encoder.get_feature_names_out(cat_cols)
    X_train_cat_df = pd.DataFrame(X_train_cat_encoded, columns=encoded_cat_names, index=X_train.index)
    X_test_cat_df = pd.DataFrame(X_test_cat_encoded, columns=encoded_cat_names, index=X_test.index)
    
    # Scale Numerical
    scaler = StandardScaler()
    X_train_num_scaled = scaler.fit_transform(X_train_num)
    X_test_num_scaled = scaler.transform(X_test_num)
    X_train_num_df = pd.DataFrame(X_train_num_scaled, columns=num_cols, index=X_train.index)
    X_test_num_df = pd.DataFrame(X_test_num_scaled, columns=num_cols, index=X_test.index)
    
    X_train_processed = pd.concat([X_train_num_df, X_train_cat_df], axis=1)
    X_test_processed = pd.concat([X_test_num_df, X_test_cat_df], axis=1)
    
    # Save preprocessors
    preprocessor = {
        'num_cols': num_cols,
        'cat_cols': cat_cols,
        'num_imputer': num_imputer,
        'cat_imputer': cat_imputer,
        'scaler': scaler,
        'encoder': encoder,
        'target_mapping': target_mapping,
        'inverse_target_mapping': {v: k for k, v in target_mapping.items()}
    }
    joblib.dump(scaler, 'models/scaler.pkl')
    joblib.dump(encoder, 'models/encoder.pkl')
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    
    # Define models
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=6, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1),
        'XGBoost': XGBClassifier(eval_metric='mlogloss', random_state=42, n_jobs=-1),
        'Support Vector Machine': SVC(probability=True, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42)
    }
    
    results = []
    
    # Binarize labels for multi-class ROC curve
    from sklearn.preprocessing import label_binarize
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
    colors = ['#10b981', '#f59e0b', '#f43f5e'] # Success, Warning, Danger
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_processed, y_train)
        
        # Save individual model file
        filename = name.lower().replace(' ', '_')
        joblib.dump(model, f'models/{filename}.pkl')
        
        # Predictions
        preds = model.predict(X_test_processed)
        probs = model.predict_proba(X_test_processed)
        
        # Metrics
        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, average='weighted')
        rec = recall_score(y_test, preds, average='weighted')
        f1 = f1_score(y_test, preds, average='weighted')
        auc_score = roc_auc_score(y_test, probs, multi_class='ovr', average='weighted')
        
        import datetime
        results.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1 Score': f1,
            'ROC-AUC': auc_score,
            'Training Date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Dataset Size': len(X_train) + len(X_test)
        })
        
        # Generate Confusion Matrix
        plt.figure(figsize=(6, 5))
        cm = confusion_matrix(y_test, preds)
        sns.heatmap(
            cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=target_mapping.keys(),
            yticklabels=target_mapping.keys()
        )
        plt.title(f'Confusion Matrix - {name}', fontsize=12, pad=10)
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        plt.tight_layout()
        plt.savefig(f'static/images/confusion_matrix_{filename}.png', dpi=150)
        plt.close()
        
        # Generate ROC Curve
        plt.figure(figsize=(6, 5))
        for i, (label_name, color) in enumerate(zip(target_mapping.keys(), colors)):
            fpr, tpr, _ = roc_curve(y_test_bin[:, i], probs[:, i])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, color=color, lw=2, label=f'{label_name} (AUC = {roc_auc:.2f})')
        plt.plot([0, 1], [0, 1], 'k--', lw=1)
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {name}', fontsize=12, pad=10)
        plt.legend(loc="lower right", fontsize=8)
        plt.grid(alpha=0.2)
        plt.tight_layout()
        plt.savefig(f'static/images/roc_curve_{filename}.png', dpi=150)
        plt.close()
        
        # Generate Feature Importance Plot
        importances = None
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.mean(np.abs(model.coef_), axis=0)
            
        if importances is not None:
            feat_importances = pd.Series(importances, index=X_train_processed.columns)
            grouped_importances = {}
            for col in num_cols:
                grouped_importances[col] = feat_importances.get(col, 0)
            for col in cat_cols:
                cat_features = [c for c in feat_importances.index if c.startswith(col + '_')]
                grouped_importances[col] = feat_importances[cat_features].sum()
                
            grouped_df = pd.Series(grouped_importances).sort_values(ascending=False).head(10)
            
            plt.figure(figsize=(8, 5))
            sns.barplot(x=grouped_df.values, y=grouped_df.index, palette='crest')
            plt.title(f'Top 10 Feature Importances - {name}', fontsize=12, pad=10)
            plt.xlabel('Relative Importance')
            plt.ylabel('Feature')
            plt.tight_layout()
            plt.savefig(f'static/images/feature_importance_{filename}.png', dpi=150)
            plt.close()
        else:
            # Create a blank placeholder graph for models without importance attributes
            plt.figure(figsize=(8, 5))
            plt.text(0.5, 0.5, "Feature Importance Not Supported", ha='center', va='center', fontsize=12)
            plt.tight_layout()
            plt.savefig(f'static/images/feature_importance_{filename}.png', dpi=150)
            plt.close()
            
    # Save the best model as general credit_model.pkl for fallback support
    results_df = pd.DataFrame(results).sort_values(by='F1 Score', ascending=False)
    best_model_name = results_df.iloc[0]['Model']
    best_filename = best_model_name.lower().replace(' ', '_')
    
    best_model = joblib.load(f'models/{best_filename}.pkl')
    joblib.dump(best_model, 'models/credit_model.pkl')
    
    # Save comparison metrics as JSON
    results_df.to_json('models/model_comparison.json', orient='records')
    print("\nTraining completed successfully! Comparison table saved.")
    print(results_df.to_string(index=False))

if __name__ == '__main__':
    train_and_evaluate()
