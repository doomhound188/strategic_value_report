# ConnectWise Ticket Summarizer

This tool fetches your ConnectWise tickets, notes, and time entries, and uses Google's Gemini AI to generate a quarterly work summary.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment**:
    - Copy `.env.example` to `.env`:
        ```bash
        cp .env.example .env
        ```
    - Edit `.env` and fill in your details:
        - `CW_COMPANY_ID`: Your ConnectWise Company ID
        - `CW_SITE_URL`: AWS URL e.g., `api-na.myconnectwise.net`
        - `CW_PUBLIC_KEY` & `CW_PRIVATE_KEY`: API Keys from "My Account" > "API Keys"
        - `CW_MEMBER_ID`: Your username (to filter tickets where you are the owner)
        - `GOOGLE_API_KEY`: API Key from Google AI Studio

## Usage

Run the script:

```bash
python main.py
```

- The script defaults to fetching tickets from `2024-01-01` onwards.
- It will process 20 tickets by default (for safety/testing). You can change `MAX_TICKETS` in `main.py` when ready for a full run.
- The output will be displayed in the console and saved to `quarterly_summary.md`.

## Troubleshooting

- **401 Unauthorized**: Check your Company ID and Keys.
- **No tickets found**: Check if `CW_MEMBER_ID` is correct (matches the `owner` field in CW). You can try removing the member ID check in `main.py` to fetch all tickets to debug.
