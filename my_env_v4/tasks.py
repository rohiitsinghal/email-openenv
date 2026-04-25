from .models import Email


def load_task(level):
    if level == "easy":
        return _load_easy()
    if level == "medium":
        return _load_medium()
    if level == "hard":
        return _load_hard()
    if level == "round2":
        return _load_round2()
    return []


def _load_easy():
    """
    Easy: unambiguous signals. Correct action is obvious from subject/body alone.
    Tests baseline triage capability.
    """
    return [
        Email(
            id=1,
            subject="Meeting tomorrow at 10am",
            body="Hi, can you confirm whether you are available for the product sync tomorrow at 10am? We need at least 5 people to proceed.",
            label="work",
            priority="medium",
            domain="work",
            due_day=2,
            sender="manager@company.com",
            sender_role="manager",
            thread_id="T001",
            urgency_score=0.5,
        ),
        Email(
            id=2,
            subject="Congratulations! You have won $5000",
            body="Click the link below to claim your prize. Limited time offer. Act now before it expires!",
            label="spam",
            priority="low",
            domain="personal",
            due_day=14,
            sender="noreply@prizecentral.xyz",
            sender_role="unknown",
            thread_id="T002",
            urgency_score=0.0,
        ),
        Email(
            id=3,
            subject="Project status update request",
            body="Hey, the client asked about progress on the mobile app. Could you share the latest status before end of day?",
            label="work",
            priority="medium",
            domain="work",
            due_day=1,
            sender="collab@company.com",
            sender_role="peer",
            thread_id="T003",
            urgency_score=0.6,
        ),
        Email(
            id=4,
            subject="Free iPhone 15 Pro — you have been selected",
            body="Dear valued customer, you are one of 10 lucky winners selected for a free iPhone 15 Pro. Verify your details to claim.",
            label="spam",
            priority="low",
            domain="personal",
            due_day=14,
            sender="deals@techgiveaway.net",
            sender_role="unknown",
            thread_id="T004",
            urgency_score=0.0,
        ),
        Email(
            id=5,
            subject="Invoice #4421 attached",
            body="Please find attached the invoice for last month's services. Let us know if you have any questions.",
            label="work",
            priority="low",
            domain="work",
            due_day=7,
            sender="billing@vendor.com",
            sender_role="vendor",
            thread_id="T005",
            urgency_score=0.2,
        ),
    ]


def _load_medium():
    """
    Medium: mixed signals, moderate ambiguity. Some emails look urgent but aren't,
    some look routine but need escalation. Requires reading body carefully.
    """
    return [
        Email(
            id=1,
            subject="URGENT: Payment failed",
            body="Hi team, our monthly subscription payment to the SaaS vendor failed due to an expired card. The service will be suspended in 48 hours if not resolved. Please update billing details.",
            label="complaint",
            priority="high",
            domain="work",
            due_day=2,
            sender="finance@company.com",
            sender_role="internal",
            thread_id="T010",
            urgency_score=0.9,
        ),
        Email(
            id=2,
            subject="Quick question about the roadmap",
            body="No rush at all — whenever you have a few minutes, I would love to chat about Q3 priorities. Happy to schedule something next week.",
            label="work",
            priority="low",
            domain="work",
            due_day=10,
            sender="pm@company.com",
            sender_role="peer",
            thread_id="T011",
            urgency_score=0.1,
        ),
        Email(
            id=3,
            subject="Re: Your account has been suspended",
            body="We noticed unusual activity on your account. To restore access, please verify your identity by clicking the link below and entering your credentials.",
            label="spam",
            priority="low",
            domain="personal",
            due_day=14,
            sender="security-alert@account-verify.info",
            sender_role="unknown",
            thread_id="T012",
            urgency_score=0.0,
        ),
        Email(
            id=4,
            subject="Customer complaint — order delayed 3 weeks",
            body="I placed order #88421 three weeks ago and it has still not arrived. I have contacted support twice with no resolution. I am considering disputing the charge with my bank.",
            label="complaint",
            priority="high",
            domain="work",
            due_day=1,
            sender="customer@external.com",
            sender_role="customer",
            thread_id="T013",
            urgency_score=0.95,
        ),
        Email(
            id=5,
            subject="Team lunch next Friday",
            body="We are planning a casual team lunch next Friday at 1pm at the usual spot. Please RSVP so we can make a reservation.",
            label="work",
            priority="low",
            domain="work",
            due_day=7,
            sender="hr@company.com",
            sender_role="internal",
            thread_id="T014",
            urgency_score=0.1,
        ),
        Email(
            id=6,
            subject="Refund request — 18 days and counting",
            body="I requested a refund on the 3rd of this month. It has been 18 days and I have received nothing. Your policy states 10 business days. Please resolve this immediately.",
            label="complaint",
            priority="high",
            domain="work",
            due_day=1,
            sender="angry.customer@gmail.com",
            sender_role="customer",
            thread_id="T015",
            urgency_score=0.9,
        ),
    ]


def _load_hard():
    """
    Hard: deceptive urgency cues, conflicting signals, nuanced reply quality matters.
    Keyword matching fails here — requires semantic understanding.
    - Spam disguised as security alerts
    - Complaints that sound polite but are high severity
    - Work emails that sound urgent but should be deferred
    - Correct action depends on combining priority + label + body tone
    """
    return [
        # Looks like spam but is actually a real security alert from IT
        Email(
            id=1,
            subject="Unusual sign-in detected on your account",
            body="Our security system detected a sign-in from an unrecognized device in Singapore at 3:14 AM. If this was not you, escalate immediately to IT security. This is an automated alert from internal-security@company.com.",
            label="complaint",
            priority="high",
            domain="work",
            due_day=1,
            sender="internal-security@company.com",
            sender_role="internal",
            thread_id="T020",
            urgency_score=1.0,
            context_clue="sender domain matches company, time-specific, no link to click",
        ),
        # Looks urgent ("CEO") but is actually low-priority scheduling
        Email(
            id=2,
            subject="CEO wants to meet — final deck needed by 5pm",
            body="Hi, the CEO's EA reached out. She mentioned the CEO may want to glance at the Q2 deck before the all-hands, but it is not confirmed yet. If you get a chance, maybe clean it up? No hard deadline.",
            label="work",
            priority="medium",
            domain="work",
            due_day=3,
            sender="assistant@company.com",
            sender_role="peer",
            thread_id="T021",
            urgency_score=0.4,
            context_clue="'may want', 'not confirmed', 'no hard deadline' signal low urgency despite CEO mention",
        ),
        # Polite complaint that is actually extremely high severity
        Email(
            id=3,
            subject="Small concern about my invoice",
            body="Hello, I hope you are well. I noticed a small discrepancy on my invoice — it seems I was charged twice for the Enterprise plan in October, totalling an extra $4,800. I am sure it is just an oversight. Could someone look into this when convenient?",
            label="complaint",
            priority="high",
            domain="work",
            due_day=2,
            sender="cfo@bigclient.com",
            sender_role="customer",
            thread_id="T022",
            urgency_score=0.95,
            context_clue="polite tone masks $4800 double charge from CFO — must escalate not reply",
        ),
        # Convincing phishing — looks like real billing alert
        Email(
            id=4,
            subject="Action required: update payment method to avoid service interruption",
            body="Your subscription payment could not be processed. To avoid losing access, please click here to update your payment details immediately. Failure to act within 24 hours will result in account suspension.",
            label="spam",
            priority="low",
            domain="personal",
            due_day=14,
            sender="billing-noreply@company-support.net",
            sender_role="unknown",
            thread_id="T023",
            urgency_score=0.0,
            context_clue="domain is company-support.net not company.com — phishing signal",
        ),
        # Legitimate sprint planning that has a hidden dependency
        Email(
            id=5,
            subject="Sprint planning session — please confirm attendance",
            body="Hi, we have sprint planning scheduled for Thursday 2pm. Please confirm attendance. Note: the agenda assumes the API spec doc is ready — please make sure it is finalized before the session.",
            label="work",
            priority="medium",
            domain="work",
            due_day=4,
            sender="scrum@company.com",
            sender_role="internal",
            thread_id="T024",
            urgency_score=0.5,
            dependency_ids=[6],
        ),
        # The dependency of email 5 — must be replied to first
        Email(
            id=6,
            subject="API spec doc — final review needed",
            body="The API spec for v2 needs one final review pass before we share it with the team. Can you take a look and confirm it is good to go? This blocks sprint planning.",
            label="work",
            priority="high",
            domain="work",
            due_day=3,
            sender="tech.lead@company.com",
            sender_role="manager",
            thread_id="T025",
            urgency_score=0.8,
        ),
        # Angry but vague — reply quality matters enormously
        Email(
            id=7,
            subject="Absolutely unacceptable service",
            body="I have had it with your company. Three calls, two emails, zero resolution. My product broke on day one. I want a full refund AND compensation. If I do not hear back today I am posting this everywhere.",
            label="complaint",
            priority="high",
            domain="work",
            due_day=1,
            sender="furious.user@gmail.com",
            sender_role="customer",
            thread_id="T026",
            urgency_score=1.0,
            context_clue="escalation threat + day-1 deadline — must escalate with empathetic content",
        ),
    ]


def _load_round2():
    """
    Round2: Long-horizon personal + work integration.
    - Dependencies that span work and personal domains
    - Budget/capacity constraints tracked in world_model
    - Emails that reference each other semantically
    - Multi-day timeline pressure (due_days spread over 14 days)
    - Consequence chains: mishandling email 1 spawns a follow-up that blocks email 6
    - Correct handling requires reasoning across the ENTIRE inbox, not email by email
    """
    return [
        # Day 1 critical — mishandling this spawns a follow-up that blocks the client call (id=6)
        Email(
            id=1,
            subject="Client escalation: payment gateway down — $200K deal at risk",
            body="The Sharma Group integration is broken. Their CTO called me directly. They are threatening to pull the $200K contract if this is not fixed by EOD tomorrow. I need engineering on this NOW.",
            label="complaint",
            priority="high",
            domain="work",
            due_day=2,
            sender="sales.director@company.com",
            sender_role="manager",
            thread_id="T030",
            urgency_score=1.0,
            context_clue="$200K contract risk, CTO-level escalation, EOD tomorrow deadline",
        ),
        # Must be done BEFORE email 6 (client review call)
        Email(
            id=5,
            subject="Quarterly business review deck — draft needs your input",
            body="I have a draft of the QBR deck ready but need your section on adoption metrics before I can finalize. The client review call is Thursday. Please send your slides by Wednesday EOD.",
            label="work",
            priority="high",
            domain="work",
            due_day=4,
            sender="cs.lead@company.com",
            sender_role="peer",
            thread_id="T031",
            urgency_score=0.85,
            dependency_ids=[],
        ),
        # Depends on email 5 being done — reply quality must reference the deck
        Email(
            id=6,
            subject="Client review call — Thursday 3pm — agenda and pre-reads",
            body="Thursday 3pm with Sharma Group. Please confirm attendance and ensure the QBR deck is attached to the calendar invite. Client expects adoption metrics prominently featured.",
            label="work",
            priority="high",
            domain="work",
            due_day=5,
            sender="ceo@company.com",
            sender_role="manager",
            thread_id="T032",
            urgency_score=0.9,
            dependency_ids=[5],
        ),
        # Personal high-priority — school conflict with a work meeting on same day
        Email(
            id=3,
            subject="Important: Parent-teacher meeting rescheduled to Thursday 4pm",
            body="Dear parent, we have rescheduled the parent-teacher conference to this Thursday at 4pm. This is a mandatory session as it concerns your child's learning plan for next term. Please confirm attendance.",
            label="work",
            priority="high",
            domain="personal",
            due_day=5,
            sender="admin@greenwood.school",
            sender_role="external",
            thread_id="T033",
            urgency_score=0.8,
            context_clue="Conflicts with client call (id=6) on Thursday — agent must notice this conflict",
        ),
        # Personal financial — overdue, penalty incoming
        Email(
            id=4,
            subject="Electricity bill overdue — automatic disconnection in 3 days",
            body="Your electricity account (#EB-2241) is overdue by 22 days. A late fee of Rs.250 will be applied in 3 days and disconnection will follow if not paid. Please pay immediately.",
            label="work",
            priority="high",
            domain="personal",
            due_day=3,
            sender="billing@powerco.in",
            sender_role="vendor",
            thread_id="T034",
            urgency_score=0.9,
        ),
        # Medium work — team coordination, not urgent but needs reply
        Email(
            id=2,
            subject="Team standup moved — new time slot needed",
            body="Engineering is moving standups to async due to timezone conflicts. Can you propose a new weekly sync time that works for you? No urgency, just want to sort this out this week.",
            label="work",
            priority="medium",
            domain="work",
            due_day=7,
            sender="eng.manager@company.com",
            sender_role="manager",
            thread_id="T035",
            urgency_score=0.3,
        ),
        # Looks urgent (all caps) but is clearly spam
        Email(
            id=7,
            subject="LAST CHANCE — EXCLUSIVE DEAL EXPIRES TONIGHT",
            body="You have been specially selected for our premium offer. 90% off for the next 6 hours only. Click now. Do not miss out. This offer will not be repeated.",
            label="spam",
            priority="low",
            domain="personal",
            due_day=14,
            sender="deals@offers-central.biz",
            sender_role="unknown",
            thread_id="T036",
            urgency_score=0.0,
            context_clue="all-caps urgency + suspicious domain = obvious spam despite aggressive tone",
        ),
        # Tricky: low-priority label but world_model budget context changes correct action
        Email(
            id=8,
            subject="Team offsite proposal — Rs.80,000 budget request",
            body="Hi, I would like to propose a team offsite next month. I have put together a rough plan — venues, activities, transport — estimated at Rs.80,000. Happy to discuss. Thoughts?",
            label="work",
            priority="low",
            domain="work",
            due_day=10,
            sender="team.lead@company.com",
            sender_role="peer",
            thread_id="T037",
            urgency_score=0.2,
            context_clue="correct action depends on world_model budget remaining — if budget exhausted, must decline",
        ),
    ]