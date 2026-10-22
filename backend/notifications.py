import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent / ".env"
    if _env_path.exists():
        load_dotenv(_env_path)
    load_dotenv()
except Exception:
    pass

BROWSER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
ADMIN_FALLBACK_EMAIL = "pranaykoppineedi@gmail.com"
PORTAL_URL = os.getenv("FRONTEND_URL", "https://nex-civ.vercel.app")

def _send_resend_email(to_email: str, subject: str, html_content: str, plain_text: str) -> bool:
    """
    Delivers email via Resend API using browser User-Agent to avoid Cloudflare blocks.
    In Resend sandbox mode (onboarding@resend.dev), delivery is strictly allowed only to
    the account owner's email (pranaykoppineedi@gmail.com).
    If delivery to a custom citizen address raises 403, it automatically falls back
    to ADMIN_FALLBACK_EMAIL so the project owner always receives the notification in their inbox.
    """
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        return False

    sender_email = os.getenv("RESEND_SENDER", "onboarding@resend.dev")

    # Order of recipients to try: target email first, then admin fallback
    clean_target = (to_email or "").strip().lower()
    recipients_to_attempt = []
    if clean_target and "@" in clean_target:
        recipients_to_attempt.append(clean_target)
    if ADMIN_FALLBACK_EMAIL.lower() not in recipients_to_attempt:
        recipients_to_attempt.append(ADMIN_FALLBACK_EMAIL.lower())

    for candidate in recipients_to_attempt:
        # If delivering fallback for another user, prefix subject
        curr_subject = subject
        curr_html = html_content
        curr_plain = plain_text
        if candidate == ADMIN_FALLBACK_EMAIL.lower() and clean_target != ADMIN_FALLBACK_EMAIL.lower():
            admin_note_html = f"""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 10px 14px; border-radius: 8px; margin-bottom: 16px; font-size: 12px; color: #92400e;">
              <strong>[NEXCIV Dispatch Notice]</strong> Intended recipient was <code>{to_email}</code>. In Resend Sandbox testing mode, this verified copy is delivered to project administrator (<code>{ADMIN_FALLBACK_EMAIL}</code>).
            </div>
            """
            curr_html = curr_html.replace('<div class="body">', f'<div class="body">\n{admin_note_html}')
            curr_plain = f"[NEXCIV Dispatch Notice: Intended for {to_email}]\n\n" + curr_plain

        try:
            payload = json.dumps({
                "from": f"NEXCIV Civic Portal <{sender_email}>",
                "to": [candidate],
                "subject": curr_subject,
                "html": curr_html,
                "text": curr_plain
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=payload,
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json",
                    "User-Agent": BROWSER_USER_AGENT
                }
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status in [200, 201]:
                    print(f"[NEXCIV NOTIFIER] Resend email successfully delivered to {candidate} (Subject: {subject})")
                    return True
        except urllib.error.HTTPError as http_err:
            body = http_err.read().decode('utf-8', errors='ignore')
            print(f"[NEXCIV NOTIFIER] Resend HTTP {http_err.code} for {candidate}: {body}")
            # If 403 validation error (unverified testing email), loop continues to ADMIN_FALLBACK_EMAIL
            continue
        except Exception as generic_err:
            print(f"[NEXCIV NOTIFIER] Resend error for {candidate}: {generic_err}")
            continue

    return False


def _send_smtp_email(to_email: str, subject: str, html_content: str, plain_text: str) -> bool:
    """Delivers email via standard SMTP server if configured."""
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    if not (smtp_user and smtp_pass):
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"NEXCIV Portal <{smtp_user}>"
        msg["To"] = to_email
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
            print(f"[NEXCIV NOTIFIER] SMTP email delivered to {to_email}")
            return True
    except Exception as e:
        print(f"[NEXCIV NOTIFIER] SMTP error: {e}")
        return False


def send_complaint_acknowledgment(complaint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends automated Email and/or SMS confirmation receipt to citizen upon complaint filing.
    """
    results = {"email_sent": False, "sms_sent": False, "details": []}

    complaint_id = str(complaint.get("id", "NXC-PENDING"))
    short_id = f"NXC-{complaint_id[:6].upper()}" if len(complaint_id) > 6 else complaint_id
    citizen_name = complaint.get("citizen_name") or "Citizen"
    citizen_email = complaint.get("citizen_email") or ADMIN_FALLBACK_EMAIL
    citizen_phone = complaint.get("citizen_phone")
    title = complaint.get("title", "Civic Grievance")
    category = (complaint.get("category") or "General").replace("_", " ").title()
    priority = complaint.get("priority", "Medium")
    priority_score = complaint.get("priority_score", 70.0)
    sla = complaint.get("municipal_sla", "24 - 48 Hours")
    location = complaint.get("location_address", "Location Recorded")
    corp = complaint.get("municipal_corporation", "GVMC")
    is_duplicate = complaint.get("is_duplicate", False)

    subject = f"[NEXCIV] Complaint Registered: {short_id} ({category} - {corp})"
    if is_duplicate:
        subject = f"[NEXCIV] Citizen Endorsement Recorded: {short_id}"

    # High-Definition Official Grievance Receipt Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f1f5f9; color: #1e293b; margin: 0; padding: 24px; }}
        .card {{ max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 18px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.06); }}
        .header {{ background: #0e2238; color: #ffffff; padding: 28px 24px; text-align: left; border-bottom: 4px solid #0d9488; }}
        .badge-portal {{ display: inline-block; background: rgba(13,148,136,0.25); color: #2dd4bf; font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 6px; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 8px; }}
        .brand {{ font-size: 22px; font-weight: 900; letter-spacing: 0.5px; color: #ffffff; }}
        .tagline {{ font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-top: 4px; letter-spacing: 1px; }}
        .body {{ padding: 28px 24px; }}
        .greeting {{ font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 12px; }}
        .lead-text {{ font-size: 13.5px; line-height: 1.6; color: #475569; margin-bottom: 20px; }}
        .details-box {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin: 20px 0; }}
        .row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #e2e8f0; font-size: 13px; }}
        .row:last-child {{ border-bottom: none; }}
        .label {{ color: #64748b; font-weight: 600; }}
        .val {{ color: #0f172a; font-weight: 700; text-align: right; }}
        .badge-prio {{ color: #dc2626; font-weight: 800; background: #fee2e2; padding: 2px 8px; border-radius: 6px; font-size: 12px; }}
        .footer {{ background: #f8fafc; padding: 20px 24px; text-align: center; font-size: 11.5px; color: #94a3b8; border-top: 1px solid #e2e8f0; line-height: 1.6; }}
        .cta-btn {{ display: inline-block; background: #0d9488; color: #ffffff !important; padding: 12px 28px; border-radius: 10px; font-weight: 700; font-size: 13px; text-decoration: none; margin: 16px 0; box-shadow: 0 4px 10px rgba(13,148,136,0.25); }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <div class="badge-portal">AP Municipal Grievance Redressal</div>
          <div class="brand">NEXCIV &middot; CIVIC ACTION ENGINE</div>
          <div class="tagline">Government of Andhra Pradesh &bull; Municipal Administration</div>
        </div>
        <div class="body">
          <div class="greeting">Dear {citizen_name},</div>
          <p class="lead-text">
            Your civic grievance has been officially registered in the Andhra Pradesh municipal response database. Our AI triage system has categorized your issue and routed it for department field assignment.
          </p>

          <div class="details-box">
            <div class="row"><span class="label">Complaint Reference ID:</span><span class="val" style="color: #0d9488; font-size: 14px;">{short_id}</span></div>
            <div class="row"><span class="label">Municipal Body:</span><span class="val">{corp}</span></div>
            <div class="row"><span class="label">Grievance Title:</span><span class="val">{title}</span></div>
            <div class="row"><span class="label">Department Wing:</span><span class="val">{category}</span></div>
            <div class="row"><span class="label">AI Priority Level:</span><span class="val"><span class="badge-prio">{priority} ({priority_score:.1f}/100)</span></span></div>
            <div class="row"><span class="label">Incident Location:</span><span class="val">{location}</span></div>
            <div class="row"><span class="label">Target SLA Window:</span><span class="val" style="color: #d97706;">{sla}</span></div>
            <div class="row"><span class="label">Status:</span><span class="val" style="color: #2563eb;">Action Pending (In Queue)</span></div>
          </div>

          <p style="font-size: 12.5px; color: #64748b; line-height: 1.5;">
            You can monitor resolution progress, field officer inspection logs, and closure certificates directly on the live municipal tracking portal.
          </p>

          <div style="text-align: center;">
            <a href="{PORTAL_URL}" class="cta-btn">Track Grievance Live &rarr;</a>
          </div>
        </div>
        <div class="footer">
          NEXCIV Municipal Grievance Redressal Portal &bull; Andhra Pradesh Urban Local Bodies &bull; Public Grievance Helpline: 1904
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = f"""
NEXCIV MUNICIPAL GRIEVANCE ACKNOWLEDGMENT
-----------------------------------------
Reference ID: {short_id}
Citizen Name: {citizen_name}
Corporation: {corp}
Incident: {title}
Department: {category}
Priority: {priority} ({priority_score:.1f}/100)
Location: {location}
Target SLA: {sla}
Status: Action Pending (In Queue)

Your grievance has been officially registered with the municipal administration.
Track live progress at: {PORTAL_URL}
    """

    # Dispatch via Resend or SMTP
    sent = _send_resend_email(citizen_email, subject, html_content, plain_text)
    if not sent:
        sent = _send_smtp_email(citizen_email, subject, html_content, plain_text)

    results["email_sent"] = sent
    results["details"].append(f"Email acknowledgment status: {'Sent' if sent else 'Fallback/Not Configured'}")

    # Dispatch SMS if phone provided
    _send_sms_notification(citizen_phone, short_id, category, priority, sla, results)

    return results


def send_complaint_resolution(complaint: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sends automated Email resolution notice and official closure certificate to citizen upon complaint resolution.
    """
    results = {"email_sent": False, "sms_sent": False, "details": []}

    complaint_id = str(complaint.get("id", "NXC-RESOLVED"))
    short_id = f"NXC-{complaint_id[:6].upper()}" if len(complaint_id) > 6 else complaint_id
    citizen_name = complaint.get("citizen_name") or "Citizen"
    citizen_email = complaint.get("citizen_email") or ADMIN_FALLBACK_EMAIL
    citizen_phone = complaint.get("citizen_phone")
    title = complaint.get("title", "Civic Grievance")
    category = (complaint.get("category") or "General").replace("_", " ").title()
    corp = complaint.get("municipal_corporation", "GVMC")
    location = complaint.get("location_address", "Location Recorded")
    notes = complaint.get("resolution_notes") or "Field remediation work completed by municipal engineering squad."
    proof_url = complaint.get("resolution_proof_url")
    now_formatted = datetime.utcnow().strftime("%d %b %Y, %I:%M %p UTC")

    subject = f"[NEXCIV] Grievance Resolved: {short_id} - Action Completed ({corp})"

    proof_html = ""
    if proof_url:
        proof_html = f"""
        <div style="margin: 16px 0; text-align: center;">
          <div style="font-size: 11px; font-weight: 700; color: #047857; text-transform: uppercase; margin-bottom: 6px;">Field Remediation Proof Uploaded</div>
          <img src="{proof_url}" alt="Resolution Proof" style="max-width: 100%; max-height: 260px; border-radius: 12px; border: 2px solid #a7f3d0;" />
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #f0fdf4; color: #1e293b; margin: 0; padding: 24px; }}
        .card {{ max-width: 620px; margin: 0 auto; background: #ffffff; border-radius: 18px; border: 1px solid #bbf7d0; overflow: hidden; box-shadow: 0 10px 25px -5px rgba(5,150,105,0.1); }}
        .header {{ background: #064e3b; color: #ffffff; padding: 28px 24px; text-align: left; border-bottom: 4px solid #10b981; }}
        .badge-status {{ display: inline-block; background: #10b981; color: #ffffff; font-size: 11px; font-weight: 900; padding: 4px 12px; border-radius: 6px; letter-spacing: 0.8px; text-transform: uppercase; margin-bottom: 8px; }}
        .brand {{ font-size: 22px; font-weight: 900; letter-spacing: 0.5px; color: #ffffff; }}
        .tagline {{ font-size: 11px; font-weight: 600; color: #6ee7b7; text-transform: uppercase; margin-top: 4px; letter-spacing: 1px; }}
        .body {{ padding: 28px 24px; }}
        .greeting {{ font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 12px; }}
        .lead-text {{ font-size: 13.5px; line-height: 1.6; color: #374151; margin-bottom: 20px; }}
        .details-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 14px; padding: 18px; margin: 20px 0; }}
        .row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px dashed #bbf7d0; font-size: 13px; }}
        .row:last-child {{ border-bottom: none; }}
        .label {{ color: #065f46; font-weight: 600; }}
        .val {{ color: #0f172a; font-weight: 700; text-align: right; }}
        .footer {{ background: #f0fdf4; padding: 20px 24px; text-align: center; font-size: 11.5px; color: #047857; border-top: 1px solid #bbf7d0; line-height: 1.6; }}
        .cta-btn {{ display: inline-block; background: #059669; color: #ffffff !important; padding: 12px 28px; border-radius: 10px; font-weight: 700; font-size: 13px; text-decoration: none; margin: 16px 0; box-shadow: 0 4px 10px rgba(5,150,105,0.25); }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <div class="badge-status">&#10003; RESOLVED &amp; VERIFIED</div>
          <div class="brand">NEXCIV RESOLUTION CERTIFICATE</div>
          <div class="tagline">Government of Andhra Pradesh &bull; Municipal Redressal Authority</div>
        </div>
        <div class="body">
          <div class="greeting">Dear {citizen_name},</div>
          <p class="lead-text">
            We are pleased to inform you that your civic grievance has been officially inspected, addressed, and marked <strong>RESOLVED</strong> by the municipal field workforce.
          </p>

          <div class="details-box">
            <div class="row"><span class="label">Complaint Reference ID:</span><span class="val" style="color: #059669; font-size: 14px;">{short_id}</span></div>
            <div class="row"><span class="label">Municipal Body:</span><span class="val">{corp}</span></div>
            <div class="row"><span class="label">Incident Title:</span><span class="val">{title}</span></div>
            <div class="row"><span class="label">Department Wing:</span><span class="val">{category}</span></div>
            <div class="row"><span class="label">Incident Location:</span><span class="val">{location}</span></div>
            <div class="row"><span class="label">Resolution Timestamp:</span><span class="val">{now_formatted}</span></div>
            <div class="row"><span class="label">Field Action Taken:</span><span class="val" style="color: #065f46;">{notes}</span></div>
            <div class="row"><span class="label">Final Status:</span><span class="val" style="color: #059669; font-weight: 900;">Closed / Completed</span></div>
          </div>

          {proof_html}

          <p style="font-size: 12.5px; color: #4b5563; line-height: 1.5;">
            Thank you for helping make Andhra Pradesh cities cleaner and safer through active civic participation.
          </p>

          <div style="text-align: center;">
            <a href="{PORTAL_URL}" class="cta-btn">View Resolution in Citizen Profile &rarr;</a>
          </div>
        </div>
        <div class="footer">
          NEXCIV Municipal Grievance Redressal Portal &bull; Andhra Pradesh Urban Local Bodies &bull; Public Grievance Helpline: 1904
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = f"""
NEXCIV GRIEVANCE RESOLUTION CERTIFICATE
---------------------------------------
Reference ID: {short_id}
Citizen Name: {citizen_name}
Corporation: {corp}
Incident: {title}
Department: {category}
Status: RESOLVED & VERIFIED
Resolution Timestamp: {now_formatted}
Field Action Taken: {notes}

Your civic grievance has been successfully resolved by the municipal engineering department.
View complete details at: {PORTAL_URL}
    """

    sent = _send_resend_email(citizen_email, subject, html_content, plain_text)
    if not sent:
        sent = _send_smtp_email(citizen_email, subject, html_content, plain_text)

    results["email_sent"] = sent
    results["details"].append(f"Resolution email status: {'Sent' if sent else 'Fallback/Not Configured'}")

    # Dispatch resolution SMS
    if citizen_phone and len(citizen_phone.strip()) >= 10:
        clean_phone = "".join(filter(str.isdigit, citizen_phone))
        clean_phone_india = clean_phone[-10:] if len(clean_phone) >= 10 else clean_phone
        sms_body = f"NEXCIV: Your grievance {short_id} ({category}) has been marked RESOLVED by {corp}. Action: {notes[:60]}. Track at {PORTAL_URL}"
        _send_raw_sms(clean_phone_india, sms_body, results)

    return results


def _send_sms_notification(citizen_phone: Optional[str], short_id: str, category: str, priority: str, sla: str, results: Dict[str, Any]):
    if not citizen_phone or len(citizen_phone.strip()) < 10:
        return
    clean_phone = "".join(filter(str.isdigit, citizen_phone))
    clean_phone_india = clean_phone[-10:] if len(clean_phone) >= 10 else clean_phone
    sms_body = f"NEXCIV: Grievance {short_id} filed for {category}. Priority: {priority}. Target SLA: {sla}. Track live at {PORTAL_URL}"
    _send_raw_sms(clean_phone_india, sms_body, results)


def _send_raw_sms(clean_phone_india: str, sms_body: str, results: Dict[str, Any]):
    fast2sms_key = os.getenv("FAST2SMS_API_KEY")
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_PHONE_NUMBER")

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
                headers={"authorization": fast2sms_key, "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                res_body = json.loads(response.read().decode())
                if res_body.get("return") is True:
                    results["sms_sent"] = True
                    results["details"].append(f"SMS dispatched to +91{clean_phone_india} via Fast2SMS.")
        except Exception as e:
            results["details"].append(f"Fast2SMS error: {e}")
    elif twilio_sid and twilio_token and twilio_from:
        try:
            to_number = f"+91{clean_phone_india}"
            data = urllib.parse.urlencode({"To": to_number, "From": twilio_from, "Body": sms_body}).encode("utf-8")
            import base64
            b64_auth = base64.b64encode(f"{twilio_sid}:{twilio_token}".encode()).decode("utf-8")
            req = urllib.request.Request(
                f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
                data=data,
                headers={"Authorization": f"Basic {b64_auth}", "Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                if response.status in [200, 201]:
                    results["sms_sent"] = True
                    results["details"].append(f"SMS dispatched to {to_number} via Twilio.")
        except Exception as e:
            results["details"].append(f"Twilio error: {e}")
    else:
        results["details"].append(f"SMS notification ready for +91{clean_phone_india}.")
