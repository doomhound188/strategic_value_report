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

## Usage

The easiest way to run the application is using the pre-built container from GitHub Container Registry.

### 1. Configure Environment
Create a `.env` file with your ConnectWise and AI credentials (see `.env.example`).

### 2. Run with Podman/Docker

```bash
# Pull the latest image
podman pull ghcr.io/doomhound188/strategic_value_report:latest

# Run the container (background)
podman run -d -p 5000:5000 --env-file .env ghcr.io/doomhound188/strategic_value_report:latest
```

Access the interface at `http://localhost:5000`.

## Local Development

To run locally directly with Python:

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the script**:
    ```bash
    python app.py
    ```

-   The script defaults to fetching tickets from `2024-01-01` onwards.
-   It will process a subset of tickets by default (controlled by `MAX_TICKETS` in `main.py`).
-   The output will be saved to **`quarterly_summary.md`**.

## Troubleshooting

-   **401 Unauthorized**: Check your Company ID and Keys.
-   **No tickets found**: Check if `CW_MEMBER_ID` is correct (matches the `owner` field in CW).
