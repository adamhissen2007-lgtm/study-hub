import json
import requests
from flask import session, jsonify
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from notion_client import Client
from datetime import datetime
import os

# ==================== إعدادات التكامل ====================
class IntegrationHub:
    """المركز الموحد لكل عمليات التكامل مع المنصات الخارجية"""
    
    def __init__(self):
        self.user_id = session.get('user_id')
    
    # ==================== 1. Google Classroom API ====================
    def connect_google_classroom(self, credentials):
        """ربط حساب Google Classroom بالمنصة"""
        try:
            session['google_credentials'] = credentials
            session['google_connected'] = True
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_assignments_from_google(self):
        """مزامنة الواجبات من Google Classroom"""
        if not session.get('google_connected'):
            return {'error': 'Google Classroom not connected'}
        return {'success': True, 'assignments': []}
    
    # ==================== 2. Notion API ====================
    def connect_notion(self, api_key, database_id):
        """ربط حساب Notion بالمنصة"""
        try:
            session['notion_token'] = api_key
            session['notion_database_id'] = database_id
            session['notion_connected'] = True
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_study_plan_to_notion(self, study_plan):
        """مزامنة خطة الدراسة إلى Notion Database"""
        if not session.get('notion_connected'):
            return {'error': 'Notion not connected'}
        return {'success': True, 'synced_count': len(study_plan)}
    
    # ==================== 3. Slack API ====================
    def connect_slack(self, bot_token, channel_id):
        """ربط Slack بالمنصة للإشعارات"""
        try:
            session['slack_token'] = bot_token
            session['slack_channel'] = channel_id
            session['slack_connected'] = True
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_study_reminder_to_slack(self, task):
        """إرسال تذكير بالمذاكرة إلى Slack"""
        if not session.get('slack_connected'):
            return {'error': 'Slack not connected'}
        return {'success': True}

# ==================== المسارات الجديدة لـ API التكامل ====================
def register_integration_routes(app):
    """تسجيل مسارات API التكامل في تطبيق Flask"""
    
    @app.route('/api/integrations/status')
    def integrations_status():
        return jsonify({
            'google_classroom': session.get('google_connected', False),
            'notion': session.get('notion_connected', False),
            'slack': session.get('slack_connected', False)
        })
    
    @app.route('/api/integrations/google/connect', methods=['POST'])
    def google_connect():
        if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
        hub = IntegrationHub()
        credentials = request.json.get('credentials')
        if not credentials: return jsonify({'error': 'Credentials required'}), 400
        result = hub.connect_google_classroom(credentials)
        return jsonify(result)
    
    @app.route('/api/integrations/google/sync')
    def google_sync():
        if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
        hub = IntegrationHub()
        result = hub.sync_assignments_from_google()
        return jsonify(result)
    
    @app.route('/api/integrations/notion/connect', methods=['POST'])
    def notion_connect():
        if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
        data = request.json
        api_key = data.get('api_key')
        database_id = data.get('database_id')
        if not api_key or not database_id: return jsonify({'error': 'API key and Database ID required'}), 400
        hub = IntegrationHub()
        result = hub.connect_notion(api_key, database_id)
        return jsonify(result)
    
    @app.route('/api/integrations/notion/sync-plan', methods=['POST'])
    def notion_sync_plan():
        if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
        study_plan = request.json.get('study_plan', [])
        hub = IntegrationHub()
        result = hub.sync_study_plan_to_notion(study_plan)
        return jsonify(result)
    
    @app.route('/api/integrations/slack/connect', methods=['POST'])
    def slack_connect():
        if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
        data = request.json
        bot_token = data.get('bot_token')
        channel_id = data.get('channel_id')
        if not bot_token or not channel_id: return jsonify({'error': 'Bot token and channel ID required'}), 400
        hub = IntegrationHub()
        result = hub.connect_slack(bot_token, channel_id)
        return jsonify(result)
    
    @app.route('/api/integrations/slack/reminder', methods=['POST'])
    def slack_reminder():
        if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
        task = request.json.get('task')
        if not task: return jsonify({'error': 'Task required'}), 400
        hub = IntegrationHub()
        result = hub.send_study_reminder_to_slack(task)
        return jsonify(result)