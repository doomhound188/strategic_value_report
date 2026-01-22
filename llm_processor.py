import os

class LLMProcessor:
    """Multi-provider LLM processor supporting Gemini, OpenAI, and Anthropic."""
    
    PROVIDERS = {
        'gemini': {
            'name': 'Google Gemini',
            'env_key': 'GOOGLE_API_KEY',
            'models': ['gemini-2.0-flash-001', 'gemini-2.0-flash-thinking-exp-01-21', 'gemini-2.0-pro-exp-02-05', 'gemini-1.5-pro']
        },
        'openai': {
            'name': 'OpenAI',
            'env_key': 'OPENAI_API_KEY',
            'models': ['gpt-4o', 'gpt-4o-mini', 'o1-mini', 'o3-mini']
        },
        'anthropic': {
            'name': 'Anthropic',
            'env_key': 'ANTHROPIC_API_KEY',
            'models': ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022']
        }
    }
    
    def __init__(self, provider='gemini', model=None):
        self.provider = provider.lower()
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Supported: {list(self.PROVIDERS.keys())}")
        
        config = self.PROVIDERS[self.provider]
        
        # Use provided model or default to the first one in the list
        self.model = model if model else config['models'][0]
        
        if model and model not in config['models']:
            # Optional: Allow custom models or warn, but for now we'll allow it passed through
            pass

        api_key = os.getenv(config['env_key'])
        
        if not api_key:
            raise ValueError(f"Missing {config['env_key']} in environment variables.")
        
        # Initialize the appropriate client
        if self.provider == 'gemini':
            from google import genai
            self.client = genai.Client(api_key=api_key)
        elif self.provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        elif self.provider == 'anthropic':
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
    
    @classmethod
    def get_available_providers(cls):
        """Return list of available providers and their models based on configured API keys."""
        available = []
        for key, config in cls.PROVIDERS.items():
            if os.getenv(config['env_key']):
                # Flatten the list: Return unique entry for each model
                for model in config['models']:
                    available.append({
                        'id': f"{key}:{model}",
                        'provider': key,
                        'name': f"{config['name']} - {model}",
                        'model': model
                    })
        return available
    
    def _build_prompt(self, ticket_data, technician_name="the employee"):
        """Build the prompt from ticket data."""
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
        
        return f"""
        You are a Strategic Business Analyst specializing in translating technical work into business value for performance reviews.
        
        You are creating a Strategic Value Report for **{technician_name}** to be used in their performance review.
        
        Your objective is to transform the provided ConnectWise ticket data into a compelling business case that demonstrates Return on Investment (ROI) and value to the organization.
        
        **Data Provided:**
        Ticket summaries, notes, and time logs for {technician_name}.
        
        **Instructions:**
        Generate a **Strategic Value Report** that highlights achievements and contributions. Do not just list tasks. Translate technical work into **business value** and **organizational impact**.
        
        Structure the output as follows:
        
        ### 1. 💰 Direct Financial Impact & ROI
        *   Identify automations, fixes, or projects that saved time/money or protected revenue.
        *   **Quantify the value** where possible: e.g., "Automated X process, saving Y hours annually."
        *   Highlight risks mitigated that could have cost the company clients or reputation.
        
        ### 2. 🏛️ Strategic Contributions & Team Enablement
        *   Show how {technician_name} enables others to be more productive (mentoring, documentation, tool creation).
        *   Highlight collaborative work and knowledge sharing.
        *   Position contributions that elevate the entire team's output.
        
        ### 3. 🛡️ Critical Infrastructure & Reliability
        *   List the key wins where {technician_name} prevented downtime, resolved critical issues, or maintained system stability.
        *   Emphasize reliability and dependability in handling important systems.
        
        ### 4. 🚀 Innovation & Growth Initiatives
        *   Highlight work on new technologies, process improvements, or forward-thinking projects.
        *   Frame contributions that position the company for future success.

        ### 5. 💎 Professional Excellence
        *   Highlight instances demonstrating professionalism, initiative, and commitment.
        *   Include examples of going above and beyond, taking ownership, and continuous improvement.
        
        **Tone:** Professional, objective, and executive-level. Present facts with clear business context.
        **Focus:** Demonstrate the tangible value {technician_name} brings to the organization.
        
        Data:
        {full_text}
        """
    
    def summarize_quarterly_work(self, ticket_data, technician_name="the employee"):
        """
        Generate a strategic value report from ticket data.
        ticket_data: List of dicts containing ticket info, notes, and time.
        technician_name: Name of the technician for the report.
        """
        prompt = self._build_prompt(ticket_data, technician_name)
        
        if self.provider == 'gemini':
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            return response.text
        
        elif self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic business analyst and career negotiation consultant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        
        elif self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
    
    @classmethod
    def get_available_providers(cls):
        """Return list of available providers based on configured API keys."""
        available = []
        for key, config in cls.PROVIDERS.items():
            if os.getenv(config['env_key']):
                available.append({
                    'id': key,
                    'name': config['name'],
                    'model': config['model']
                })
        return available
