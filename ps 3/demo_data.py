"""
Demo data for B2B meeting summarizer
Contains realistic meeting transcripts for different enterprise scenarios
"""

def get_mock_meetings():
    """
    Returns a list of mock B2B meeting scenarios for demo purposes.
    Each meeting contains client_name, project_name, and detailed transcript.
    """
    
    mock_meetings = [
        {
            "client_name": "TechCorp Solutions",
            "project_name": "Digital Transformation Initiative",
            "transcript": """
Meeting started at 2:00 PM EST. Attendees: Sarah Chen (Project Manager), Mike Rodriguez (Lead Developer), Jennifer Wu (Client Stakeholder), David Kim (UX Designer).

Sarah opened the meeting: "Welcome everyone. Today we're reviewing the Q3 milestones for TechCorp's digital transformation project. Jennifer, how are things looking from your end?"

Jennifer responded: "The executive team is very pleased with the progress. However, we need to accelerate the mobile app development timeline. Can we move the deadline from December 15th to November 30th?"

Mike interjected: "That's quite aggressive. We'd need additional resources. Sarah, can we bring in two more developers?"

Sarah noted: "I'll reach out to the resource pool immediately. Mike, you must prioritize the core authentication features first. David, perhaps you could finalize the mobile wireframes by October 20th?"

David agreed: "Absolutely. I'll also coordinate with Jennifer's internal design team next week."

Jennifer added: "Excellent work everyone. One concern - the budget is approaching 85% utilization. We need to be more careful with scope creep."

Sarah concluded: "Mike will handle the technical architecture review by Friday. Jennifer, please confirm the revised timeline with your executives. David will present updated designs to stakeholders next Tuesday."

Meeting ended at 3:15 PM EST.
            """
        },
        {
            "client_name": "GlobalBank Financial",
            "project_name": "Risk Management System Upgrade",
            "transcript": """
Conference call initiated at 10:00 AM. Participants: Alex Thompson (Risk Manager), Lisa Zhang (Security Architect), Robert Garcia (Client CTO), Emma Johnson (Compliance Officer).

Alex started: "Good morning everyone. We're here to discuss the critical security patches for GlobalBank's risk management system. Robert, what's the current status on your end?"

Robert explained: "We've identified three high-priority vulnerabilities that must be addressed immediately. The regulatory audit is scheduled for next month, so timing is crucial."

Lisa responded: "I've already begun the security assessment. Alex, we need to schedule the penetration testing for this week. Can you coordinate with the ops team?"

Emma interrupted: "From a compliance perspective, we're looking good, but the documentation needs updating. Lisa, someone should probably review the security protocols by Wednesday."

Alex assigned tasks: "Robert will provide the system access credentials by tomorrow. Lisa must complete the vulnerability assessment by Thursday. Emma, perhaps you could draft the compliance report for the auditors?"

Robert emphasized: "This is critical priority. Any delays could result in regulatory penalties. Lisa, do you need additional team members?"

Lisa confirmed: "Two additional security specialists would help. Emma, great work on the preliminary compliance review."

Robert concluded: "Let's schedule a follow-up for Friday to review progress. Alex will coordinate with all stakeholders."

Call ended at 11:20 AM.
            """
        },
        {
            "client_name": "MedTech Innovations",
            "project_name": "Healthcare Platform Integration",
            "transcript": """
Video conference began at 3:30 PM PST. Present: Dr. Amanda Foster (Clinical Director), Tom Wilson (Software Engineer), Rachel Adams (Client Product Manager), Carlos Mendez (Data Analyst).

Dr. Foster opened: "Thank you all for joining. We're discussing the integration of patient data systems for MedTech's new healthcare platform. Rachel, how are we progressing?"

Rachel updated: "The platform is 70% complete, but we're facing some data privacy challenges. Tom, the HIPAA compliance module needs immediate attention."

Tom acknowledged: "I understand the urgency. Dr. Foster, we'll need your clinical team to validate the data workflows. Can someone from your team review the specifications by next Friday?"

Dr. Foster confirmed: "Absolutely. I'll assign Dr. Martinez to lead that review. Carlos, excellent analysis on the patient data patterns last week."

Carlos responded: "Thank you. I've identified some optimization opportunities. Rachel, perhaps we could schedule a data workshop for your team next week?"

Rachel agreed: "That sounds valuable. Tom, the client is requesting a demo for their board meeting on November 8th. We must have the core features ready."

Tom committed: "I'll prioritize the patient portal functionality. Dr. Foster, will your team be available for user acceptance testing next Tuesday?"

Dr. Foster confirmed: "Yes, we'll provide feedback on the clinical workflows. Tom, great work on the security implementation so far."

Rachel summarized: "Carlos will prepare the data integration timeline by Wednesday. Tom must deliver the demo-ready version by November 5th. Dr. Foster will coordinate clinical testing."

Meeting concluded at 4:45 PM PST.
            """
        },
        {
            "client_name": "RetailMax Corporation",
            "project_name": "E-commerce Platform Modernization",
            "transcript": """
In-person meeting started at 1:00 PM. Attendees: Mark Stevens (E-commerce Director), Anna Rodriguez (Full-Stack Developer), Kevin Liu (Client Operations Manager), Sophie Turner (Marketing Coordinator).

Mark began: "Welcome to our weekly sync. We're focusing on RetailMax's e-commerce platform modernization. Kevin, how's the stakeholder feedback looking?"

Kevin reported: "The executive team loves the new checkout process, but they're concerned about the Black Friday readiness. Can we ensure everything is stable by November 15th?"

Anna responded: "The core platform is solid, but we need to conduct load testing. Mark, someone should probably coordinate with the infrastructure team this week."

Sophie added: "From a marketing perspective, the new product recommendation engine is performing excellently. Anna, fantastic work on the machine learning integration."

Mark assigned: "Kevin will finalize the Black Friday promotional requirements by Thursday. Anna must complete the performance optimization by next Monday. Sophie, perhaps you could prepare the marketing automation setup?"

Kevin emphasized: "This is moderate priority, but customer experience is critical during peak season. Anna, do you need additional database support?"

Anna confirmed: "One additional DevOps engineer would be helpful. Kevin, the analytics dashboard improvements look great."

Sophie suggested: "We should schedule a full-system test next week. Mark will coordinate with all departments?"

Mark agreed: "Absolutely. Kevin will handle the stakeholder communications. Anna must deliver the final performance report by Friday. Sophie will launch the pre-Black Friday email campaigns."

Kevin concluded: "Outstanding progress everyone. Let's reconvene Thursday to finalize the go-live strategy."

Meeting ended at 2:20 PM.
            """
        }
    ]
    
    return mock_meetings

def get_meeting_by_index(index):
    """
    Returns a specific mock meeting by index (0-3).
    Useful for demo purposes to quickly select different scenarios.
    """
    meetings = get_mock_meetings()
    if 0 <= index < len(meetings):
        return meetings[index]
    return None

def get_all_client_names():
    """
    Returns a list of all client names for quick reference.
    """
    meetings = get_mock_meetings()
    return [meeting["client_name"] for meeting in meetings]

def get_all_project_names():
    """
    Returns a list of all project names for quick reference.
    """
    meetings = get_mock_meetings()
    return [meeting["project_name"] for meeting in meetings]