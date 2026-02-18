# CTI_DAHSBOARD

**Project Overview**

This project is a Cyber Threat Intelligence (CTI) Dashboard that collects, processes, and visualizes threat indicators such as IP addresses, domains, and malware hashes.

The system provides:

Threat severity distribution

Threat type analysis

Indicator listings

Statistical summaries

**System Architecture**

The CTI Dashboard follows a three-layer architecture:

1️⃣ Data Layer

Stores Cyber Threat Intelligence (CTI) data

JSON-based dataset

Located inside /data

Contains:

Threat indicators (IP, domain, hash)

Severity

Source

Timestamps

2️⃣ Backend Layer

Built using Python (Flask / FastAPI)

Reads CTI JSON dataset

Exposes REST APIs:

/api/threats

/api/stats

Performs filtering and aggregation

Located inside /backend

3️⃣ Frontend Layer

Built using React

Fetches data from backend APIs

Displays:

Severity distribution charts

Threat type charts

Indicator tables

Located inside /frontend

🔄 Data Flow

CTI data is stored in JSON format.

Backend reads and processes the data.

Backend exposes APIs.

Frontend calls APIs.

User views visual dashboard.
