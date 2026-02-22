Frontend folder for React dashboard
# CTI Dashboard – Frontend

## Overview

This frontend application is part of the Cyber Threat Intelligence (CTI) Platform.  
It provides an interactive dashboard that visualizes cyber threat intelligence data collected from open-source CTI feeds.

The dashboard converts raw threat data into meaningful insights using charts, tables, and filtering mechanisms.

---

## Objective

The objective of this frontend module is to:

- Display cyber threat intelligence data visually
- Provide severity and type-based analysis
- Show threat trends over time
- Enable filtering of threats
- Prepare the UI for backend API integration

---

## Tech Stack

- HTML
- CSS
- JavaScript
- Chart.js
- REST API (for backend integration)

---

## Features Implemented

- Dashboard layout UI
- Threat Type Distribution (Bar Chart)
- Severity Distribution (Pie Chart)
- Threat Trend Over Time (Line Chart)
- Recent Threat Activity Table
- Severity Filter
- Static data rendering
- Placeholder API fetch logic
- Responsive design improvements

---

## Planned API Endpoints

The frontend is prepared to consume the following backend APIs:

- GET /threats
- GET /stats
- GET /threats?severity=high
- POST /auth/login

---

## How to Run

1. Clone the repository
2. Navigate to the frontend folder
3. Open index.html in a browser

OR

Use Live Server extension in VS Code.

---

## Future Improvements

- Connect to live backend APIs
- Add authentication UI
- Add advanced filtering
- Improve UI/UX design

---

## Developer

Sarika  
Frontend Engineer – CTI Platform