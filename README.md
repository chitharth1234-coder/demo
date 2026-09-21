# BOB AI Rescue — Hackathon Prototype

## What this prototype demonstrates

A simulated production incident goes through:

Incident Detection
→ Multi-Agent Investigation
→ Root Cause Analysis
→ Impact Analysis
→ Rescue Plan
→ What-If Simulation
→ Automated Validation
→ Human Approval
→ Deployment
→ Post-Rescue Monitoring

## Run locally

1. Install Python.
2. Open a terminal in this folder.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the app:

```bash
streamlit run app.py
```

## Demo flow

1. Open the Command Center.
2. Click **Simulate Production Incident**.
3. Open **AI Investigation**.
4. Click **Run Parallel Investigation**.
5. Open **Root Cause**.
6. Open **Rescue Plan**.
7. Click **Run Rescue Simulation**.
8. Click **Approve Rescue**.
9. Click **Deploy Rescue**.
10. Open **Monitoring** and show the recovered system.

This is a controlled simulation for a hackathon prototype. The incident, metrics and AI findings are intentionally simulated so the workflow can be demonstrated reliably.
