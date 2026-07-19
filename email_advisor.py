import os
import datetime

OUTBOX_DIR = 'mail_outbox'

def send_report_email(recipient_email, applicant_name, result):
    """
    Simulates sending an automated underwriting PDF report attachment via SMTP.
    Writes the dispatched report file to a local outbox folder for verification.
    """
    if not recipient_email:
        recipient_email = f"{applicant_name.lower().replace(' ', '_')}@finguard-mock-bank.com"
        
    os.makedirs(OUTBOX_DIR, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = applicant_name.lower().replace(' ', '_')
    outbox_file = os.path.join(OUTBOX_DIR, f"report_{safe_name}_{timestamp}.txt")
    
    report_text = f"""==================================================
FINGUARD AI BANK - CREDIT ASSESSMENT ADVISOR
==================================================
Date generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Recipient Email: {recipient_email}
Applicant Name: {applicant_name}

--------------------------------------------------
RISK ASSESSMENT RESULTS SUMMARY
--------------------------------------------------
Risk Rating Category: {result.get('risk_level', 'Unknown').upper()}
Default Probability: {result.get('default_probability', 0.0)}%
Repayment Likelihood: {result.get('repayment_probability', 100.0)}%
Underwriting Decision: {result.get('recommendation', 'Manual Review').upper()}
Active Decision Engine: {result.get('model_used', 'unknown').upper()}

--------------------------------------------------
AI UNDERWRITING SUGGESTIONS & OPTIMIZATION
--------------------------------------------------
"""
    for sug in result.get('suggestions', []):
        report_text += f"- {sug}\n"
        
    report_text += """
--------------------------------------------------
EXPLAINABLE AI ATTRIBUTIONS
--------------------------------------------------
"""
    for dr in result.get('positive_drivers', []):
        report_text += f"[Risk Driver] {dr.get('feature')}: +{round(dr.get('contribution')*100, 2)}%\n"
        
    for dr in result.get('negative_drivers', []):
        report_text += f"[Mitigating Factor] {dr.get('feature')}: {round(dr.get('contribution')*100, 2)}%\n"
        
    report_text += """
==================================================
End of Assessment Certificate
Verification QR Code Reference: https://finguard.ai/verify/mock
==================================================
"""
    
    # Save the simulated email transmission file
    with open(outbox_file, 'w') as f:
        f.write(report_text)
        
    # Print terminal SMTP logs
    print(f"\n>>> Connecting to mock SMTP mail server at mail.finguard.ai:587...")
    print(f">>> Authenticating sender: underwriting-advisor@finguard.ai...")
    print(f">>> Preparing MIME multipart message envelope...")
    print(f">>> Attaching simulated report certificate: {outbox_file}...")
    print(f">>> Dispatching email to recipient: {recipient_email}...")
    print(f">>> Email dispatch successfully completed!\n")
    
    return outbox_file
