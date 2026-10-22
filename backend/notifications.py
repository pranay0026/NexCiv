import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import urllib.request
import urllib.parse
import urllib.error

def send_complaint_acknowledgment(complaint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends automated Email and/or SMS confirmation receipt to citizen upon complaint filing.
    Supports:
      1. Email: Resend API (HTTP) OR standard SMTP (Gmail/Outlook)
      2. SMS: Fast2SMS (India Quick SMS) OR Twilio (Global SMS)
      3. Fallback: Local simulation log when credentials are not yet configured in .env
    """
    results = {"email_sent": False, "sms_sent": False, "details": []}
    
    complaint_id = complaint.get("id", "NXC-PENDING")
    short_id = f"NXC-{complaint_id[:6].upper()}" if len(complaint_id) > 6 else complaint_id
    citizen_name = complaint.get("citizen_name") or "Citizen"
    citizen_email = complaint.get("citizen_email")
    citizen_phone = complaint.get("citizen_phone")
    title = complaint.get("title", "Civic Grievance")
    category = (complaint.get("category") or "General").replace("_", " ").title()
    priority = complaint.get("priority", "Medium")
    sla = complaint.get("municipal_sla", "48 - 72 Hours")
    location = complaint.get("location_address", "Location Recorded")
    is_duplicate = complaint.get("is_duplicate", False)

    # -------------------------------------------------------------
    # 1. EMAIL NOTIFICATION DISPATCH
    # -------------------------------------------------------------
    if citizen_email and "@" in citizen_email:
        email_sent = False
        resend_key = os.getenv("RESEND_API_KEY")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))

        subject = f"[NEXCIV] Complaint Registered: {short_id} ({category})"
        if is_duplicate:
            subject = f"[NEXCIV] Citizen Endorsement Recorded: {short_id}"

        # High-definition HTML Municipal Receipt
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f4f7fa; color: #1e293b; margin: 0; padding: 20px; }}
            .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .header {{ background: #0e2238; color: #ffffff; padding: 24px; text-align: left; }}
            .brand {{ font-size: 20px; font-weight: 900; letter-spacing: 0.5px; color: #ffffff; }}
            .tagline {{ font-size: 11px; font-weight: 700; color: #2dd4bf; text-transform: uppercase; margin-top: 4px; }}
            .body {{ padding: 24px; }}
            .greeting {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; }}
            .details-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin: 16px 0; }}
            .row {{ display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px dashed #e2e8f0; font-size: 13px; }}
            .row:last-child {{ border-bottom: none; }}
            .label {{ color: #64748b; font-weight: 500; }}
            .val {{ color: #0f172a; font-weight: 700; text-align: right; }}
            .badge-prio {{ color: #0d9488; font-weight: 800; }}
            .footer {{ background: #f8fafc; padding: 16px 24px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
            .cta-btn {{ display: inline-block; background: #0d9488; color: #ffffff !important; padding: 12px 24px; border-radius: 8px; font-weight: 700; font-size: 13px; text-decoration: none; margin-top: 16px; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <div class="brand">NEXCIV &middot; CIVIC ACTION ENGINE</div>
              <div class="tagline">Automated Grievance Redressal System</div>
            </div>
            <div class="body">
              <div class="greeting">Dear {citizen_name},</div>
              <p style="font-size: 13px; line-height: 1.6; color: #475569;">
                Your civic grievance has been officially registered with the municipal response system. Our automated AI engine has classified and routed your issue to the concerned field department.
              </p>
              
              <div class="details-box">
                <div class="row"><span class="label">Complaint Reference ID:</span><span class="val" style="color: #0d9488;">{short_id}</span></div>
                <div class="row"><span class="label">Incident Title:</span><span class="val">{title}</span></div>
                <div class="row"><span class="label">Assigned Department:</span><span class="val">{category}</span></div>
                <div class="row"><span class="label">AI Priority Level:</span><span class="val badge-prio">{priority}</span></div>
                <div class="row"><span class="label">Location:</span><span class="val">{location}</span></div>
                <div class="row"><span class="label">Municipal SLA Target:</span><span class="val" style="color: #d97706;">{sla}</span></div>
                <div class="row"><span class="label">Status:</span><span class="val" style="color: #2563eb;">Pending Action</span></div>
              </div>

              <p style="font-size: 12px; color: #64748b;">
                You will receive real-time updates as our municipal field crew reviews, dispatches, and resolves this grievance.
              </p>
              
              <div style="text-align: center;">
                <a href="http://localhost:5173" class="cta-btn">View Live Grievance Status &rarr;</a>
              </div>
            </div>
            <div class="footer">
              NEXCIV Municipal Grievance Redressal Portal &middot; Government of Andhra Pradesh &middot; Urban Local Bodies
            </div>
          </div>
        </body>
        </html>
        """

        plain_text = f"""
NEXCIV Municipal Grievance Acknowledgment
Reference ID: {short_id}
Citizen Name: {citizen_name}
Incident: {title}
Department: {category}
Priority: {priority}
Location: {location}
SLA Target: {sla}

Your grievance is registered with the municipal administration. Track progress at http://localhost:5173
        """

        # Method A: Resend API (HTTP POST)
        if resend_key:
            try:
                sender_email = os.getenv("RESEND_SENDER", "onboarding@resend.dev")
                payload = json.dumps({
                    "from": f"NEXCIV Civic Portal <{sender_email}>",
                    "to": [citizen_email],
                    "subject": subject,
                    "html": html_content,
                    "text": plain_text
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://api.resend.com/emails",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {resend_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "NEXCIV-Notifier/1.0"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    if response.status in [200, 201]:
                        email_sent = True
                        results["details"].append(f"Email delivered to {citizen_email} via Resend API.")
            except Exception as e_resend:
                results["details"].append(f"Resend API error: {e_resend}")

        # Method B: Standard SMTP (e.g. Gmail App Password)
        elif smtp_user and smtp_pass:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"NEXCIV Portal <{smtp_user}>"
                msg["To"] = citizen_email
                msg.attach(MIMEText(plain_text, "plain"))
                msg.attach(MIMEText(html_content, "html"))

                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, citizen_email, msg.as_string())
                    email_sent = True
                    results["details"].append(f"Email delivered to {citizen_email} via SMTP ({smtp_host}).")
            except Exception as e_smtp:
                results["details"].append(f"SMTP error: {e_smtp}")

        # Method C: Simulator mode
        else:
            print(f"\n============================================================")
            print(f"[NOTIFICATION SIMULATOR] EMAIL ACKNOWLEDGMENT QUEUED")
            print(f"To: {citizen_email} ({citizen_name})")
            print(f"Subject: {subject}")
            print(f"Tracking ID: {short_id} | SLA: {sla}")
            print(f"Tip: Set RESEND_API_KEY or SMTP_USER & SMTP_PASSWORD in backend/.env to deliver live emails.")
            print(f"============================================================\n")
            results["details"].append(f"Simulated email delivery to {citizen_email} (configure RESEND_API_KEY or SMTP in backend/.env for live transmission).")
            email_sent = True

        results["email_sent"] = email_sent

    # -------------------------------------------------------------
    # 2. SMS NOTIFICATION DISPATCH
    # -------------------------------------------------------------
    if citizen_phone and len(citizen_phone.strip()) >= 10:
        clean_phone = "".join(filter(str.isdigit, citizen_phone))
        # Default Indian mobile format: 10 digits
        if len(clean_phone) == 10:
            clean_phone_india = clean_phone
        elif len(clean_phone) > 10 and clean_phone.startswith("91"):
            clean_phone_india = clean_phone[2:]
        else:
            clean_phone_india = clean_phone

        sms_body = f"NEXCIV: Grievance {short_id} filed for {category}. Priority: {priority}. Target SLA: {sla}. Track live at http://localhost:5173"
        sms_sent = False

        fast2sms_key = os.getenv("FAST2SMS_API_KEY")
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_from = os.getenv("TWILIO_PHONE_NUMBER")

        # Method A: Fast2SMS (Direct Indian Transactional/Quick SMS)
        if fast2sms_key:
            try:
                payload = json.dumps({
                    "route": "q",
                    "message": sms_body,
                    "flash": 0,
                    "numbers": clean_phone_india
                }).encode("utf-8")
                req = urllib.request.Request(
                    "https://www.fast2sms.com/dev/bulkV2",
                    data=payload,
                    headers={
                        "authorization": fast2sms_key,
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    res_body = json.loads(response.read().decode())
                    if res_body.get("return") is True:
                        sms_sent = True
                        results["details"].append(f"SMS dispatched to +91{clean_phone_india} via Fast2SMS.")
                    else:
                        results["details"].append(f"Fast2SMS API notice: {res_body.get('message')}")
            except Exception as e_f2s:
                results["details"].append(f"Fast2SMS error: {e_f2s}")

        # Method B: Twilio (Global SMS)
        elif twilio_sid and twilio_token and twilio_from:
            try:
                to_number = f"+91{clean_phone_india}" if not clean_phone.startswith("+") else clean_phone
                data = urllib.parse.urlencode({
                    "To": to_number,
                    "From": twilio_from,
                    "Body": sms_body
                }).encode("utf-8")
                
                auth_str = f"{twilio_sid}:{twilio_token}"
                import base64
                b64_auth = base64.b64encode(auth_str.encode()).decode("utf-8")
                
                req = urllib.request.Request(
                    f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
                    data=data,
                    headers={
                        "Authorization": f"Basic {b64_auth}",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    if response.status in [200, 201]:
                        sms_sent = True
                        results["details"].append(f"SMS dispatched to {to_number} via Twilio.")
            except Exception as e_twilio:
                results["details"].append(f"Twilio error: {e_twilio}")

        # Method C: Simulator mode
        else:
            print(f"\n============================================================")
            print(f"[NOTIFICATION SIMULATOR] SMS ALERT DISPATCHED")
            print(f"To: +91 {clean_phone_india}")
            print(f"Content: \"{sms_body}\"")
            print(f"Tip: Set FAST2SMS_API_KEY (for India) or TWILIO_ACCOUNT_SID in backend/.env for live mobile transmission.")
            print(f"============================================================\n")
            results["details"].append(f"Simulated SMS alert to +91 {clean_phone_india} (configure FAST2SMS_API_KEY in backend/.env for live transmission).")
            sms_sent = True

        results["sms_sent"] = sms_sent

    return results
