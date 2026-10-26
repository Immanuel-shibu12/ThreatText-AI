"""
Generates standard sample demonstration emails in both .txt and RFC 822 .eml format
as specified in Section 7 of the ThreatText AI Blueprint.
"""

import os

SAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))

samples = [
    {
        "id": "demo_bank_verification",
        "name": "1. Bank Account Verification (Phishing)",
        "expected": "Phishing",
        "subject": "URGENT: Temporary Suspension on Online Banking Access",
        "sender": "Chase Security Alerts <service-notice@chase-secure-verify.net>",
        "recipient": "customer@gmail.com",
        "date": "Mon, 26 Oct 2026 09:14:22 -0500",
        "body": """Dear Valued Customer,

We have detected multiple unauthorized login attempts to your Chase online banking portal from an unrecognized IP address (194.26.29.112). 

For your security, access to your funds and bill payment features has been temporarily suspended. 

To restore your access immediately and avoid permanent account lock within 24 hours, you must verify your identity and confirm your account password using our secure verification server:

http://chase-identity-auth-portal.com/login?verify=true&session=89327498234

Failure to verify within 24 hours will result in permanent suspension and a $50 administrative reactivation fee.

Sincerely,
Chase Customer Protection & Fraud Operations Department
"""
    },
    {
        "id": "demo_college_timetable",
        "name": "2. College Timetable Announcement (Legitimate)",
        "expected": "Legitimate",
        "subject": "Fall Semester Final Examination Schedule and Room Assignments",
        "sender": "Academic Affairs <registrar@university.edu>",
        "recipient": "all-students@university.edu",
        "date": "Fri, 23 Oct 2026 14:30:00 -0400",
        "body": """Dear Students and Faculty,

The revised final examination schedule for the Fall 2026 academic term has now been finalized and published.

Please review your registered course codes and corresponding examination halls on the student portal before Friday, November 14th. If you identify any direct scheduling conflicts (such as two exams at the identical time slot), please submit a conflict resolution form to the registrar's office.

Key Deadlines:
- Examination conflict submission: November 5, 2026
- Reading days: November 28 - December 1, 2026
- Final exam week begins: December 2, 2026

Best wishes with your academic preparations and project submissions.

Regards,
Office of the University Registrar
Department of Academic Affairs
University Hall, Room 204
"""
    },
    {
        "id": "demo_delivery_credentials",
        "name": "3. Delivery Notification Requesting Credentials (Phishing)",
        "expected": "Phishing",
        "subject": "Parcel Delivery Exception: Incomplete Address - Action Required",
        "sender": "DHL Express Tracking <tracking-update@dhl-delivery-service.com>",
        "recipient": "imman@outlook.com",
        "date": "Sun, 25 Oct 2026 16:45:10 +0000",
        "body": """Dear Customer,

Your inbound express package (Tracking ID: #US-8891024-DHL) could not be delivered to your registered delivery address due to missing postal details and unpaid import customs duties ($2.95 USD).

Our courier attempted delivery on October 25th at 11:20 AM but was unable to complete drop-off.

To reschedule your shipment delivery and update your delivery credentials, please click the link below:

http://dhl-express-redelivery.org/track/confirm-address?pkg=US8891024

Please note: If payment and credentials are not submitted within 48 hours, the parcel will be returned to the international sender at your expense.

Thank you for choosing DHL Worldwide Express.
"""
    },
    {
        "id": "demo_workplace_meeting",
        "name": "4. Normal Workplace Meeting Invitation (Legitimate)",
        "expected": "Legitimate",
        "subject": "Q4 Sprint Planning and Product Roadmap Sync - Next Tuesday at 2 PM",
        "sender": "Marcus Vance <m.vance@techcorp-solutions.com>",
        "recipient": "engineering-team@techcorp-solutions.com",
        "date": "Wed, 21 Oct 2026 11:05:42 -0700",
        "body": """Hi Team,

Hope you're having a productive week.

I've scheduled our quarterly sprint planning and roadmap synchronization meeting for next Tuesday, October 27th, from 2:00 PM to 3:30 PM in Conference Room B (and via Google Meet for remote teammates).

Agenda:
1. Review of Q3 deliverable milestones and user engagement metrics
2. Discussion of backlog priorities for the upcoming two-week sprint
3. Architecture review for the upcoming API refactoring
4. Open Q&A and blocker resolution

Please review the attached project specification document and update your Jira tickets prior to the call so we can keep the discussion focused.

Looking forward to seeing everyone there!

Best regards,
Marcus Vance
Senior Technical Product Manager | TechCorp Solutions
"""
    },
    {
        "id": "demo_hr_payroll_update",
        "name": "5. HR Payroll & Tax Update (Advanced Phishing)",
        "expected": "Phishing",
        "subject": "ACTION REQUIRED: Mandatory W-2 Tax Information Verification",
        "sender": "Human Resources Support <hr-payroll@corporate-benefits-portal.net>",
        "recipient": "employee@company.com",
        "date": "Thu, 22 Oct 2026 08:15:33 -0400",
        "body": """Dear Employee,

In accordance with IRS end-of-year compliance regulations, all employees must review and re-verify their direct deposit payroll information and W-2 withholding forms before the upcoming payroll cut-off date.

Failure to verify your records may delay your upcoming bi-weekly paycheck and direct deposit processing.

Please sign in to the employee benefits portal below to confirm your social security number and banking details:

http://internal-portal-hr-verify.com/login?emp_id=74928

This portal will remain accessible until October 31st at 5:00 PM EST.

Sincerely,
Corporate Payroll and Benefits Administration
"""
    }
]

def generate():
    for item in samples:
        # 1. Plain text format
        txt_path = os.path.join(SAMPLES_DIR, f"{item['id']}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(f"Subject: {item['subject']}\n")
            f.write(f"From: {item['sender']}\n")
            f.write(f"To: {item['recipient']}\n")
            f.write(f"Date: {item['date']}\n\n")
            f.write(item["body"])

        # 2. RFC 822 .eml format
        eml_path = os.path.join(SAMPLES_DIR, f"{item['id']}.eml")
        with open(eml_path, "w", encoding="utf-8") as f:
            f.write(f"Subject: {item['subject']}\n")
            f.write(f"From: {item['sender']}\n")
            f.write(f"To: {item['recipient']}\n")
            f.write(f"Date: {item['date']}\n")
            f.write("MIME-Version: 1.0\n")
            f.write("Content-Type: text/plain; charset=UTF-8\n")
            f.write("Content-Transfer-Encoding: 7bit\n\n")
            f.write(item["body"])
            
    print(f"Generated {len(samples)} demo email pairs (.txt and .eml) in {SAMPLES_DIR}")

if __name__ == "__main__":
    generate()
