# CTI Dashboard – API Contract

This document defines the API structure for the CTI Dashboard project.
It ensures consistency between backend and frontend development.

--------------------------------------------------

## 1️⃣ GET /threats

Description:
Returns a list of stored threat intelligence records.
Supports filtering and pagination.

### Query Parameters (Optional)

- severity → low | medium | high | critical
- type → ip | domain | hash
- source → string
- page → number (default: 1)
- limit → number (default: 10)

Example:
GET /threats?severity=high&page=1&limit=10

### Success Response (200)

{
  "success": true,
  "total": 120,
  "page": 1,
  "limit": 10,
  "data": [
    {
      "id": "uuid",
      "ioc_type": "ip",
      "ioc_value": "192.168.1.1",
      "category": "malware",
      "severity": "high",
      "source": "AlienVault",
      "first_seen": "2026-02-01T10:00:00Z",
      "last_seen": "2026-02-10T10:00:00Z"
    }
  ]
}

### Error Response (400)

{
  "success": false,
  "message": "Invalid severity value"
}

--------------------------------------------------

## 2️⃣ GET /stats

Description:
Returns aggregated threat statistics for dashboard visualization.

### Success Response (200)

{
  "success": true,
  "data": {
    "total_threats": 1200,
    "by_severity": {
      "low": 200,
      "medium": 500,
      "high": 350,
      "critical": 150
    },
    "by_type": {
      "ip": 700,
      "domain": 300,
      "hash": 200
    }
  }
}

### Aggregation Logic

- total_threats → count of all threat records
- by_severity → grouped by severity field
- by_type → grouped by ioc_type field

--------------------------------------------------

## 3️⃣ POST /auth/login

Description:
Authenticates a user and returns a JWT token.

### Request Body

{
  "email": "user@example.com",
  "password": "password123"
}

### Success Response (200)

{
  "success": true,
  "token": "jwt_token_here"
}

### Error Response (401)

{
  "success": false,
  "message": "Invalid credentials"
}
