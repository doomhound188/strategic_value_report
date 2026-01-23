import os
import concurrent.futures
from flask import Flask, render_template, jsonify, request
from flask_session import Session
from dotenv import load_dotenv
from connectwise_client import ConnectWiseClient
from llm_processor import LLMProcessor
from auth import auth_bp, init_auth, login_required, get_current_user

load_dotenv()

app = Flask(__name__)

# Configure session for authentication
secret_key = os.getenv('FLASK_SECRET_KEY')
if not secret_key:
    app.logger.warning("FLASK_SECRET_KEY not set! Sessions will reset on restart. Set this in production.")
    secret_key = os.urandom(24).hex()

app.config['SECRET_KEY'] = secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = '/app/flask_session'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Initialize and register authentication
auth_configured = init_auth(app)
app.register_blueprint(auth_bp)

# Initialize ConnectWise client once
cw_client = None

def get_cw_client():
    global cw_client
    if cw_client is None:
        cw_client = ConnectWiseClient()
    return cw_client


@app.route('/')
@login_required
def index():
    """Serve the main web form."""
    user = get_current_user()
    return render_template('index.html', user=user)


@app.route('/api/members')
@login_required
def get_members():
    """Fetch list of ConnectWise technicians."""
    try:
        cw = get_cw_client()
        members = cw.get_members() or []
        # Return simplified member data
        result = [
            {
                'id': m.get('identifier'),
                'name': f"{m.get('firstName', '')} {m.get('lastName', '')}".strip(),
                'identifier': m.get('identifier')
            }
            for m in members
            if m.get('identifier')
        ]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/providers')
@login_required
def get_providers():
    """Get list of available LLM providers."""
    try:
        providers = LLMProcessor.get_available_providers()
        return jsonify(providers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate strategic value report."""
    try:
        data = request.json
        member_id = data.get('member_id')
        technician_name = data.get('technician_name', member_id)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        provider_id = data.get('provider', 'gemini:gemini-2.5-pro')
        
        if ':' in provider_id:
            provider, model = provider_id.split(':', 1)
        else:
            provider = provider_id
            model = None

        
        if not all([member_id, start_date, end_date]):
            return jsonify({'error': 'Missing required fields: member_id, start_date, end_date'}), 400
        
        cw = get_cw_client()
        llm = LLMProcessor(provider=provider, model=model)
        
        # Build conditions
        conditions = f'dateEntered >= [{start_date}] AND dateEntered <= [{end_date}]'
        conditions = f'(owner/identifier="{member_id}") AND ({conditions})'
        
        # Fetch tickets
        MAX_TICKETS = 1000
        service_tickets = cw.get_tickets(conditions=conditions, page_size=MAX_TICKETS) or []
        project_tickets = cw.get_project_tickets(conditions=conditions, page_size=MAX_TICKETS) or []
        tickets = service_tickets + project_tickets
        
        if not tickets:
            return jsonify({'report': '# No Tickets Found\n\nNo tickets were found for the selected criteria.'})
        
        # Process tickets concurrently
        def process_ticket(t):
            t_id = t['id']
            t_summary = t['summary']
            t_date = t.get('dateClosed') or t.get('dateEntered') or "Unknown Date"
            
            # Only fetch notes created by this technician
            notes = cw.get_ticket_notes(t_id, member_id=member_id)
            notes_text = ""
            if notes:
                notes_text = "\n".join([f"- [{n.get('dateCreated')}] {n.get('text')}" for n in notes])
            
            total_time = cw.get_total_time_for_ticket(t_id)
            
            return {
                'id': t_id,
                'summary': t_summary,
                'date': t_date,
                'notes': notes_text,
                'total_hours': total_time
            }
        
        processed_data = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_ticket, t): t for t in tickets}
            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    processed_data.append(data)
                except Exception:
                    pass  # Skip failed tickets
        
        # Generate report
        report = llm.summarize_quarterly_work(processed_data, technician_name)
        
        return jsonify({
            'report': report,
            'ticket_count': len(tickets),
            'processed_count': len(processed_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
