import requests
import requests.adapters
import base64
import os
import json

class ConnectWiseClient:
    def __init__(self):
        self.company_id = os.getenv("CW_COMPANY_ID")
        self.site_url = os.getenv("CW_SITE_URL")
        self.public_key = os.getenv("CW_PUBLIC_KEY")
        self.private_key = os.getenv("CW_PRIVATE_KEY")
        self.client_id = os.getenv("CW_CLIENT_ID")

        if not all([self.company_id, self.site_url, self.public_key, self.private_key]):
            raise ValueError("Missing ConnectWise credentials in environment variables.")

        self.base_url = f"https://{self.site_url}/v4_6_release/apis/3.0"
        
        # Prepare Auth Header
        user_pass = f"{self.company_id}+{self.public_key}:{self.private_key}"
        encoded_auth = base64.b64encode(user_pass.encode()).decode()
        
        # Use a Session for connection pooling
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=20, pool_maxsize=20)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        if self.client_id:
            self.session.headers["clientId"] = self.client_id

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error fetching {url}: {e}")
            if response.text:
                print(f"Response: {response.text}")
            return None

    def get_tickets(self, conditions=None, page=1, page_size=25):
        """
        Fetches service tickets based on conditions.
        conditions: String for CW SQL-like query e.g. "dateEntered > [2024-01-01]"
        """
        params = {
            "pageSize": page_size,
            "page": page,
            "orderBy": "dateEntered desc" 
        }
        if conditions:
            params["conditions"] = conditions
            
        return self._get("service/tickets", params=params)

    def get_project_tickets(self, conditions=None, page=1, page_size=25):
        """
        Fetches project tickets based on conditions.
        """
        params = {
            "pageSize": page_size,
            "page": page,
            "orderBy": "dateEntered desc" 
        }
        if conditions:
            params["conditions"] = conditions
            
        return self._get("project/tickets", params=params)

    def get_ticket_notes(self, ticket_id):
        return self._get(f"service/tickets/{ticket_id}/notes")

    def get_ticket_time_entries(self, ticket_id):
        # Filter time entries by ticketId
        conditions = f"ticket/id={ticket_id}"
        return self._get("time/entries", params={"conditions": conditions})

    def get_total_time_for_ticket(self, ticket_id):
        entries = self.get_ticket_time_entries(ticket_id)
        if not entries:
            return 0.0
        
        total_hours = sum(entry.get('actualHours', 0) for entry in entries)
        return total_hours
    
    def get_members(self):
        """Fetch list of active technicians/members."""
        return self._get("system/members", params={"conditions": "inactiveFlag=false", "pageSize": 1000})

