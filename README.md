# Strategic Value Report Generator

This tool transforms your raw ConnectWise service data (tickets, notes, time entries) into a high-impact **Strategic Value Report**.

Instead of a simple list of tasks, it uses **Google's Gemini 3 Pro (Preview)** to analyze your work and generate a persuasive business case tailored for:
*   **Performance Reviews**
*   **Compensation Negotiations**
*   **Promotion Justifications**

The AI acts as a "Career Negotiation Consultant," translating technical data into **Executive-Level** insights focused on ROI, financial impact, and strategic leadership.

## Key Features

*   **Automated Data Gathering**: Fetches your tickets and time entries directly from ConnectWise Manage.
*   **ROI-Focused Analysis**: Quantifies the financial impact of your work (e.g., "Saved X hours," "Protected $Y revenue").
*   **Strategic Narrative**: Organizes your contributions into four critical pillars:
    1.  💰 **Direct Financial Impact & ROI**
    2.  🏛️ **Strategic Leadership & Force Multiplication**
    3.  🛡️ **Critical Infrastructure & Stability**
    4.  🚀 **Future-Proofing & Innovation**

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

-   The script defaults to fetching tickets from `2024-01-01` onwards.
-   It will process a subset of tickets by default (controlled by `MAX_TICKETS` in `main.py`).
-   The output will be saved to **`quarterly_summary.md`**.

## Troubleshooting

-   **401 Unauthorized**: Check your Company ID and Keys.
-   **No tickets found**: Check if `CW_MEMBER_ID` is correct (matches the `owner` field in CW).
