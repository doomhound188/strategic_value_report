from google import genai
import os
import json

class LLMProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Missing GOOGLE_API_KEY in environment variables.")
        
        self.client = genai.Client(api_key=api_key)

    def summarize_quarterly_work(self, ticket_data):
        """
        ticket_data: List of dicts containing ticket info, notes, and time.
        """
        prompt_data = []
        for t in ticket_data:
            prompt_data.append(f"""
            Ticket: {t['summary']} (ID: {t['id']})
            Date: {t['date']}
            Total Hours: {t['total_hours']}
            Notes: {t['notes']}
            --------------------------------------------------
            """)
        
        full_text = "\n".join(prompt_data)
        
        prompt = f"""
        You are a high-level Career Negotiation Consultant and Strategic Business Analyst acting on behalf of **Andrew**.
        Andrew is preparing for a critical performance review with the explicit goal of **securing a significant compensation increase**.
        
        Your objective is to transform the provided ConnectWise ticket data into a powerful business case that demonstrates massive Return on Investment (ROI) and irreplaceable value to the organization.
        
        **Data Provided:**
        Ticket summaries, notes, and time logs.
        
        **Instructions:**
        Generate a **Strategic Value Report** that controls the narrative of the review. Do not just list tasks. You must translate technical work into **business value** and **financial impact**.
        
        Structure the output as follows:
        
        ### 1. 💰 Direct Financial Impact & ROI
        *   Identify automations, fixes, or projects that saved time/money or protected revenue.
        *   **Quantify the value**: e.g., "Automated X process, saving Y hours annually, equivalent to $Z in labor costs."
        *   Highlight risks mitigated that could have cost the company clients or reputation.
        
        ### 2. 🏛️ Strategic Leadership & Force Multiplication
        *   Show how Andrew enables *others* to be more productive (mentoring, documentation, tool creation).
        *   Position Andrew not just as a worker, but as a "Force Multiplier" who elevates the entire team's output.
        
        ### 3. 🛡️ Critical Infrastructure & Stability
        *   List the "Keep the Lights On" wins where Andrew prevented downtime or disasters.
        *   Emphasize reliability: "Andrew is the safety net for the department."
        
        ### 4. 🚀 Future-Proofing & Innovation
        *   Highlight work on cutting-edge tech (Rewst, AI, Security) that positions the company for future growth.
        *   Frame this as "Andrew is leading the company's technical evolution."
        
        **Tone:** Authoritative, persuasive, executive-level, and confident. 
        **Key Message:** "The business cannot afford to lose Andrew, and his contributions far exceed his current compensation."
        
        Data:
        {full_text}
        """
        
        response = self.client.models.generate_content(
            model='gemini-3-pro-preview', 
            contents=prompt
        )
        return response.text
