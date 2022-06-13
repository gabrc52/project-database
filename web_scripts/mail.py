import smtplib
from email.mime.text import MIMEText
from xml.etree.ElementTree import Comment

import db
import creds
from datetime import datetime


APPROVERS_LIST = "sipb-projectdb-approvers@mit.edu"
SERVICE_EMAIL = "sipb-projectdb-bot@mit.edu" #Email identifying as coming from this service

ACTIVE_PROJECTS_URL = "https://{locker}.scripts.mit.edu:444/projectlist.py?filter_by=active".format(locker=creds.user)

def send(recipients, sender, subject, message):
    """Send an unauthenticated email using MIT's SMTP server

    Args:
        recipients (Sequence[str] | str): If one receipient, use a single string. Else use a list of strings.
        sender (str): Email of sender
        subject (str): Email subject
        message (str): Actual content of email
    """
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    if isinstance(recipients, str):
        msg['To'] = recipients
    elif isinstance(recipients, list):
        msg['To'] = ','.join(recipients)
    else:
        raise Exception("Email reciepient neither a list or a string")
    
    s = smtplib.SMTP('outgoing.mit.edu', 25)
    s.sendmail(sender, recipients, msg.as_string())
    s.quit()


def send_to_approvers(project_info):
    """Send a message to the approver mailing list notifying that a project is
    ready for review.
    """
    project_creator = db.get_project_creator(project_info['project_id'])
    current_time = datetime.now().strftime("%H:%M:%S on %m/%d/%Y")
    subject = "Project '{name}' needs approval".format(name=project_info['name'])
    msg = """
    Dear SIPB Project Approvers,
    
    Project '{name}' has been submitted to the database by {creator} and is ready for review.
    
    This email was generated as of {time}.
    
    Sincerely,
    SIPB ProjectDB service bot
    """.format(name=project_info['name'],creator=project_creator,time=current_time)
    
    send(APPROVERS_LIST,SERVICE_EMAIL,subject,msg)

def send_approve_message(project_info, approver_kerberos, approver_comments):
    """Send a message to the project creator and points of contact indicating
    that the project has been accepted.
    """
    # Get point of contacts
    recipients = [db.get_project_creator(project_info['project_id'])]
    for contact in project_info['contacts']:
       recipients.append(contact['email'])
        
    #Send out email to project's creator and points of contacts
    current_time = datetime.now().strftime("%H:%M:%S on %m/%d/%Y")
    subject = "Project {name} has been approved".format(name=project_info['name'])
    msg = """
    Dear {name}'s project team,
    
    Congratulations! Your project submission to the SIPB projects website has been reviewed and approved by {approver}, 
    with the following comment:
    {comment}
    
    You can now find your project on the list of active projects at:
    {url}
    
    This email was generated as of {time}.
    
    Sincerely,
    SIPB ProjectDB service bot
    """.format(name=project_info['name'],
               url=ACTIVE_PROJECTS_URL,
               time=current_time,
               approver=approver_kerberos,
               comment=approver_comments if approver_comments else "None")
    send(recipients,SERVICE_EMAIL,subject,msg)


def send_reject_message(project_info, approver_kerberos, approver_comments):
    """Send a message to the project creator and points of contact indicating
    that the project has been rejected.
    """
    # Get point of contacts
    recipients = [db.get_project_creator(project_info['project_id'])]
    for contact in project_info['contacts']:
       recipients.append(contact['email'])
        
    #Send out email to project's creator and points of contacts
    current_time = datetime.now().strftime("%H:%M:%S on %m/%d/%Y")
    subject = "Project {name} has been rejected".format(name=project_info['name'])
    msg = """
    Dear {name}'s project team,
    
    Unfortunately, your project submission to the SIPB projects website has been rejected by {approver}
    with the following comments:
    {comment}
    
    If relevant, please make the necessary changes to your project submission and resubmit for another review.
    
    This email was generated as of {time}.
    
    Sincerely,
    SIPB ProjectDB service bot
    """.format(name=project_info['name'],
               url=ACTIVE_PROJECTS_URL,
               time=current_time,
               approver=approver_kerberos,
               comment=approver_comments) # There *must* be a comment for rejection
    send(recipients,SERVICE_EMAIL,subject,msg)


def send_confirm_reminder_message(project_info):
    """Send a message to the project contact(s) reminding them to confirm the
    project details.
    """
    # TODO: Not implemented yet!
    pass


def send_deactivation_message(project_info):
    """Send a message to the project contact(s) informing them that their
    project's status has been set to "inactive" and will no longer appear on
    the list of active projects.
    """
    # TODO: Not implemented yet!
    pass
