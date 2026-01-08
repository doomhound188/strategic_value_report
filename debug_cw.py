import os
import json
from dotenv import load_dotenv
from connectwise_client import ConnectWiseClient

def debug_ticket_structure():
    load_dotenv()
    cw = ConnectWiseClient()
    
    # Fetch just 1 ticket to inspect structure
    tickets = cw.get_tickets(page_size=1)
    if tickets:
        print(json.dumps(tickets[0], indent=2))
    else:
        print("No tickets found to inspect.")

if __name__ == "__main__":
    debug_ticket_structure()
