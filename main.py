import os
import time
from dotenv import load_dotenv
from connectwise_client import ConnectWiseClient
from llm_processor import LLMProcessor

def main():
    load_dotenv()
    
    # Check for member ID to filter "my" tickets
    member_id = os.getenv("CW_MEMBER_ID")
    if not member_id:
        print("Warning: CW_MEMBER_ID not set. Fetching ALL tickets (this might be a lot).")
        input("Press Enter to continue or Ctrl+C to abort...")

    print("Initializing clients...")
    try:
        cw = ConnectWiseClient()
        llm = LLMProcessor()
    except Exception as e:
        print(f"Initialization Failed: {e}")
        return

    print("Fetching tickets...")
    # Conditions: Only closed tickets? specific date? 
    # For now, let's try to get tickets where user is the owner or resource.
    # Note: "Resources" is a child list, filtering by it is harder in CW API conditions top-level.
    # Easier filter: owner/id="member_id" or simple fetch all and filter in python if volume allows.
    # Let's filter by date to keep it sane for a first run, e.g., > 2024-01-01
    
    conditions = 'dateEntered > [2025-02-01]'
    if member_id:
        conditions = f'(owner/identifier="{member_id}") AND ({conditions})'

    print(f"Querying with conditions: {conditions}")
    
    # limits
    MAX_TICKETS = 1000 # Increased for production run
    
    print("Fetching Service Tickets...")
    service_tickets = cw.get_tickets(conditions=conditions, page_size=MAX_TICKETS) or []
    print(f"Found {len(service_tickets)} service tickets.")

    print("Fetching Project Tickets...")
    project_tickets = cw.get_project_tickets(conditions=conditions, page_size=MAX_TICKETS) or []
    print(f"Found {len(project_tickets)} project tickets.")
    
    # Merge
    tickets = service_tickets + project_tickets
    
    if not tickets:
        print("No tickets found.")
        return

    print(f"Total {len(tickets)} tickets to process. Fetching details concurrently...")
    
    processed_data = []
    
    import concurrent.futures

    def process_ticket(t):
        t_id = t['id']
        t_summary = t['summary']
        # Fix KeyError: 'dateEntered' - Use .get() safely
        t_date = t.get('dateClosed') or t.get('dateEntered') or "Unknown Date"
        
        # print(f"Processing Ticket #{t_id}: {t_summary}") # Too noisy for threads
        
        # specific notes: user wants "ticket title and all associated notes"
        notes = cw.get_ticket_notes(t_id)
        notes_text = ""
        if notes:
            notes_text = "\n".join([f"- [{n.get('dateCreated')}] {n.get('text')}" for n in notes])
            
        # Time
        total_time = cw.get_total_time_for_ticket(t_id)
        
        return {
            'id': t_id,
            'summary': t_summary,
            'date': t_date,
            'notes': notes_text,
            'total_hours': total_time
        }

    # Use ThreadPoolExecutor for I/O bound parallelism
    # Be mindful of API rate limits. 10 workers is usually safe for occasional use.
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticket = {executor.submit(process_ticket, t): t for t in tickets}
        
        for i, future in enumerate(concurrent.futures.as_completed(future_to_ticket)):
            t = future_to_ticket[future]
            try:
                data = future.result()
                processed_data.append(data)
                if (i + 1) % 1 == 0:
                    print(f"[{i+1}/{len(tickets)}] Processed details for {data['summary']}")
            except Exception as exc:
                print(f"Ticket {t['id']} generated an exception: {exc}")

    print("Data collection complete. Generating Quarterly Summary...")
    
    summary = llm.summarize_quarterly_work(processed_data)
    
    print("\n========== Quarterly Report ==========\n")
    print(summary)
    
    # Save to file
    with open("quarterly_summary.md", "w", encoding="utf-8") as f:
        f.write(summary)
    print("\nSaved to quarterly_summary.md")

if __name__ == "__main__":
    main()
