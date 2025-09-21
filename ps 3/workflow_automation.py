"""
Advanced workflow automation system
Handles automated tasks, triggers, and business process automation
"""

import json
from datetime import datetime, timedelta
from enum import Enum
from models import db, User, Project, MeetingSummary, TaskAssignment, TeamMember
import logging

class TriggerType(Enum):
    """Types of workflow triggers"""
    MEETING_CREATED = "meeting_created"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_OVERDUE = "task_overdue"
    PROJECT_CREATED = "project_created"
    USER_REGISTERED = "user_registered"
    SCHEDULED = "scheduled"
    MANUAL = "manual"

class ActionType(Enum):
    """Types of workflow actions"""
    SEND_EMAIL = "send_email"
    CREATE_TASK = "create_task"
    SEND_NOTIFICATION = "send_notification"
    UPDATE_STATUS = "update_status"
    ASSIGN_USER = "assign_user"
    CREATE_REMINDER = "create_reminder"
    GENERATE_REPORT = "generate_report"
    WEBHOOK = "webhook"

class WorkflowEngine:
    """Advanced workflow automation engine"""
    
    def __init__(self):
        self.workflows = {}
        self.active_workflows = []
        self.trigger_handlers = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register default workflow templates"""
        self.workflows = {
            'meeting_follow_up': {
                'name': 'Meeting Follow-up Automation',
                'description': 'Automatically creates tasks and sends notifications after meetings',
                'trigger': TriggerType.MEETING_CREATED,
                'conditions': {
                    'meeting_type': ['project_planning', 'client_meeting', 'team_meeting']
                },
                'actions': [
                    {
                        'type': ActionType.CREATE_TASK,
                        'config': {
                            'template': 'Follow up on {meeting_type} meeting with {client_name}',
                            'priority': 'medium',
                            'due_days': 3
                        }
                    },
                    {
                        'type': ActionType.SEND_NOTIFICATION,
                        'config': {
                            'message': 'Meeting summary created for {client_name} - {project_name}',
                            'recipients': ['meeting_creator', 'project_team']
                        }
                    }
                ],
                'enabled': True
            },
            'task_reminder': {
                'name': 'Task Reminder Automation',
                'description': 'Sends reminders for overdue and upcoming tasks',
                'trigger': TriggerType.SCHEDULED,
                'schedule': 'daily',
                'conditions': {},
                'actions': [
                    {
                        'type': ActionType.SEND_NOTIFICATION,
                        'config': {
                            'message': 'Task "{task_description}" is due {due_date}',
                            'recipients': ['task_assignee']
                        }
                    }
                ],
                'enabled': True
            },
            'project_kickoff': {
                'name': 'Project Kickoff Automation',
                'description': 'Automatically sets up new projects with initial tasks',
                'trigger': TriggerType.PROJECT_CREATED,
                'conditions': {
                    'project_type': ['client_project', 'internal_project']
                },
                'actions': [
                    {
                        'type': ActionType.CREATE_TASK,
                        'config': {
                            'template': 'Project kickoff meeting with {client_name}',
                            'priority': 'high',
                            'due_days': 1
                        }
                    },
                    {
                        'type': ActionType.CREATE_TASK,
                        'config': {
                            'template': 'Create project timeline and milestones',
                            'priority': 'medium',
                            'due_days': 7
                        }
                    },
                    {
                        'type': ActionType.SEND_EMAIL,
                        'config': {
                            'template': 'project_kickoff_email',
                            'recipients': ['project_team', 'client']
                        }
                    }
                ],
                'enabled': True
            },
            'weekly_report': {
                'name': 'Weekly Report Automation',
                'description': 'Generates and sends weekly project reports',
                'trigger': TriggerType.SCHEDULED,
                'schedule': 'weekly',
                'day_of_week': 'friday',
                'conditions': {},
                'actions': [
                    {
                        'type': ActionType.GENERATE_REPORT,
                        'config': {
                            'report_type': 'weekly_summary',
                            'recipients': ['project_managers', 'clients']
                        }
                    }
                ],
                'enabled': True
            }
        }
    
    def execute_workflow(self, workflow_id, trigger_data):
        """Execute a specific workflow"""
        try:
            if workflow_id not in self.workflows:
                logging.error(f"Workflow {workflow_id} not found")
                return False
            
            workflow = self.workflows[workflow_id]
            
            if not workflow.get('enabled', True):
                logging.info(f"Workflow {workflow_id} is disabled")
                return False
            
            # Check conditions
            if not self._check_conditions(workflow.get('conditions', {}), trigger_data):
                logging.info(f"Workflow {workflow_id} conditions not met")
                return False
            
            # Execute actions
            for action in workflow.get('actions', []):
                self._execute_action(action, trigger_data)
            
            logging.info(f"Workflow {workflow_id} executed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Workflow execution failed: {e}")
            return False
    
    def trigger_workflow(self, trigger_type, data):
        """Trigger workflows based on event type"""
        try:
            triggered_workflows = []
            
            for workflow_id, workflow in self.workflows.items():
                if workflow.get('trigger') == trigger_type:
                    if self.execute_workflow(workflow_id, data):
                        triggered_workflows.append(workflow_id)
            
            return triggered_workflows
            
        except Exception as e:
            logging.error(f"Workflow triggering failed: {e}")
            return []
    
    def _check_conditions(self, conditions, trigger_data):
        """Check if workflow conditions are met"""
        try:
            for condition_key, condition_value in conditions.items():
                if condition_key in trigger_data:
                    if isinstance(condition_value, list):
                        if trigger_data[condition_key] not in condition_value:
                            return False
                    else:
                        if trigger_data[condition_key] != condition_value:
                            return False
                else:
                    return False
            
            return True
            
        except Exception as e:
            logging.error(f"Condition checking failed: {e}")
            return False
    
    def _execute_action(self, action, trigger_data):
        """Execute a workflow action"""
        try:
            action_type = ActionType(action['type'])
            config = action.get('config', {})
            
            if action_type == ActionType.SEND_EMAIL:
                self._send_email_action(config, trigger_data)
            elif action_type == ActionType.CREATE_TASK:
                self._create_task_action(config, trigger_data)
            elif action_type == ActionType.SEND_NOTIFICATION:
                self._send_notification_action(config, trigger_data)
            elif action_type == ActionType.UPDATE_STATUS:
                self._update_status_action(config, trigger_data)
            elif action_type == ActionType.ASSIGN_USER:
                self._assign_user_action(config, trigger_data)
            elif action_type == ActionType.CREATE_REMINDER:
                self._create_reminder_action(config, trigger_data)
            elif action_type == ActionType.GENERATE_REPORT:
                self._generate_report_action(config, trigger_data)
            elif action_type == ActionType.WEBHOOK:
                self._webhook_action(config, trigger_data)
            
        except Exception as e:
            logging.error(f"Action execution failed: {e}")
    
    def _send_email_action(self, config, trigger_data):
        """Send email action"""
        try:
            # This would integrate with email service
            template = config.get('template', 'default')
            recipients = self._resolve_recipients(config.get('recipients', []), trigger_data)
            
            logging.info(f"Email sent to {recipients} using template {template}")
            
        except Exception as e:
            logging.error(f"Email action failed: {e}")
    
    def _create_task_action(self, config, trigger_data):
        """Create task action"""
        try:
            template = config.get('template', 'New task')
            priority = config.get('priority', 'medium')
            due_days = config.get('due_days', 7)
            
            # Replace placeholders in template
            task_description = self._replace_placeholders(template, trigger_data)
            
            # Calculate due date
            due_date = datetime.utcnow() + timedelta(days=due_days)
            
            # Create task
            task = TaskAssignment(
                task_description=task_description,
                priority=priority,
                status='pending',
                due_date=due_date,
                project_id=trigger_data.get('project_id'),
                created_by=trigger_data.get('user_id', 1)
            )
            
            db.session.add(task)
            db.session.commit()
            
            logging.info(f"Task created: {task_description}")
            
        except Exception as e:
            logging.error(f"Create task action failed: {e}")
    
    def _send_notification_action(self, config, trigger_data):
        """Send notification action"""
        try:
            message = self._replace_placeholders(config.get('message', ''), trigger_data)
            recipients = self._resolve_recipients(config.get('recipients', []), trigger_data)
            
            # This would integrate with notification system
            logging.info(f"Notification sent to {recipients}: {message}")
            
        except Exception as e:
            logging.error(f"Notification action failed: {e}")
    
    def _update_status_action(self, config, trigger_data):
        """Update status action"""
        try:
            entity_type = config.get('entity_type', 'task')
            entity_id = trigger_data.get(f'{entity_type}_id')
            new_status = config.get('status')
            
            if entity_type == 'task' and entity_id:
                task = TaskAssignment.query.get(entity_id)
                if task:
                    task.status = new_status
                    db.session.commit()
                    logging.info(f"Task {entity_id} status updated to {new_status}")
            
        except Exception as e:
            logging.error(f"Update status action failed: {e}")
    
    def _assign_user_action(self, config, trigger_data):
        """Assign user action"""
        try:
            entity_type = config.get('entity_type', 'task')
            entity_id = trigger_data.get(f'{entity_type}_id')
            assignee_id = config.get('assignee_id')
            
            if entity_type == 'task' and entity_id and assignee_id:
                task = TaskAssignment.query.get(entity_id)
                if task:
                    task.assignee_id = assignee_id
                    db.session.commit()
                    logging.info(f"Task {entity_id} assigned to user {assignee_id}")
            
        except Exception as e:
            logging.error(f"Assign user action failed: {e}")
    
    def _create_reminder_action(self, config, trigger_data):
        """Create reminder action"""
        try:
            # This would create a reminder in the system
            reminder_time = config.get('reminder_time', '1 day')
            message = self._replace_placeholders(config.get('message', ''), trigger_data)
            
            logging.info(f"Reminder created: {message} at {reminder_time}")
            
        except Exception as e:
            logging.error(f"Create reminder action failed: {e}")
    
    def _generate_report_action(self, config, trigger_data):
        """Generate report action"""
        try:
            report_type = config.get('report_type', 'summary')
            recipients = self._resolve_recipients(config.get('recipients', []), trigger_data)
            
            # This would generate and send reports
            logging.info(f"Report generated: {report_type} for {recipients}")
            
        except Exception as e:
            logging.error(f"Generate report action failed: {e}")
    
    def _webhook_action(self, config, trigger_data):
        """Webhook action"""
        try:
            url = config.get('url')
            payload = self._replace_placeholders(config.get('payload', '{}'), trigger_data)
            
            # This would send HTTP request to webhook URL
            logging.info(f"Webhook sent to {url}: {payload}")
            
        except Exception as e:
            logging.error(f"Webhook action failed: {e}")
    
    def _replace_placeholders(self, text, data):
        """Replace placeholders in text with actual data"""
        try:
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                if placeholder in text:
                    text = text.replace(placeholder, str(value))
            
            return text
            
        except Exception as e:
            logging.error(f"Placeholder replacement failed: {e}")
            return text
    
    def _resolve_recipients(self, recipients, trigger_data):
        """Resolve recipient list"""
        try:
            resolved = []
            
            for recipient in recipients:
                if recipient == 'meeting_creator':
                    resolved.append(trigger_data.get('user_id'))
                elif recipient == 'project_team':
                    # Get project team members
                    project_id = trigger_data.get('project_id')
                    if project_id:
                        team_members = TeamMember.query.filter_by(project_id=project_id).all()
                        resolved.extend([member.user_id for member in team_members])
                elif recipient == 'task_assignee':
                    resolved.append(trigger_data.get('assignee_id'))
                else:
                    resolved.append(recipient)
            
            return list(set(resolved))  # Remove duplicates
            
        except Exception as e:
            logging.error(f"Recipient resolution failed: {e}")
            return recipients
    
    def create_custom_workflow(self, workflow_config):
        """Create a custom workflow"""
        try:
            workflow_id = f"custom_{int(datetime.utcnow().timestamp())}"
            self.workflows[workflow_id] = workflow_config
            
            logging.info(f"Custom workflow created: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logging.error(f"Custom workflow creation failed: {e}")
            return None
    
    def get_workflow_status(self, workflow_id):
        """Get workflow status and execution history"""
        try:
            if workflow_id not in self.workflows:
                return None
            
            workflow = self.workflows[workflow_id]
            
            return {
                'id': workflow_id,
                'name': workflow.get('name'),
                'enabled': workflow.get('enabled', True),
                'last_executed': workflow.get('last_executed'),
                'execution_count': workflow.get('execution_count', 0)
            }
            
        except Exception as e:
            logging.error(f"Workflow status retrieval failed: {e}")
            return None

# Global workflow engine
workflow_engine = WorkflowEngine()

def init_workflow_engine():
    """Initialize workflow engine"""
    return workflow_engine
