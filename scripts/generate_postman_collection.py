#!/usr/bin/env python3
"""
Generates Postman Collection v2.1.0 for Bharat Jyotish AI SaaS Enterprise API Gateway (/api/v1).
Includes pre-configured requests, example payloads, and token authentication headers.
"""

import json
from pathlib import Path

def build_postman_collection():
    collection = {
        "info": {
            "name": "Bharat Jyotish AI SaaS - Enterprise API v1",
            "_postman_id": "bharat-jyotish-v1-collection-2026",
            "description": "Deterministic Vedic Astrology Calculation, Inverted 12,578 Classical Rules Engine, 6-Pillar Retrospective Event Verification, and Grounded AI Consultation API Gateway.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {
                "key": "base_url",
                "value": "http://localhost:8000",
                "type": "string"
            },
            {
                "key": "jwt_token",
                "value": "",
                "type": "string"
            }
        ],
        "item": [
            {
                "name": "1. Authentication",
                "item": [
                    {
                        "name": "Login (Argon2id + JWT)",
                        "event": [
                            {
                                "listen": "test",
                                "script": {
                                    "exec": [
                                        "var jsonData = pm.response.json();",
                                        "if (jsonData.access_token) {",
                                        "    pm.collectionVariables.set('jwt_token', jsonData.access_token);",
                                        "}"
                                    ],
                                    "type": "text/javascript"
                                }
                            }
                        ],
                        "request": {
                            "method": "POST",
                            "header": [{"key": "Content-Type", "value": "application/json"}],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"username": "admin@jyotish.com", "password": "AdminPassword123!"}, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/auth/login",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "auth", "login"]
                            }
                        }
                    },
                    {
                        "name": "Get Current User Profile & Tier",
                        "request": {
                            "method": "GET",
                            "header": [
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "url": {
                                "raw": "{{base_url}}/api/v1/auth/me",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "auth", "me"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "2. Astrological Chart Calculations",
                "item": [
                    {
                        "name": "Calculate Full Natal Kundali (D1 to D10, Ashtakavarga)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "name": "Test Native",
                                    "birth_date": "1995-05-15",
                                    "birth_time": "14:30:00",
                                    "latitude": 28.6139,
                                    "longitude": 77.2090,
                                    "timezone_offset": 5.5,
                                    "ayanamsa": "Lahiri"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/charts/calculate?ayanamsa=Lahiri",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "charts", "calculate"],
                                "query": [{"key": "ayanamsa", "value": "Lahiri"}]
                            }
                        }
                    }
                ]
            },
            {
                "name": "3. Retrospective Past Event Verification (6 Pillars)",
                "item": [
                    {
                        "name": "Verify Past Event (e.g. Marriage Inquiry)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "birth_data": {
                                        "name": "Test Native",
                                        "birth_date": "1995-05-15",
                                        "birth_time": "14:30:00",
                                        "latitude": 28.6139,
                                        "longitude": 77.2090,
                                        "timezone_offset": 5.5
                                    },
                                    "target_event_date": "2021-12-10",
                                    "event_category": "marriage",
                                    "natural_query_text": "क्या मेरी शादी हो चुकी है?",
                                    "ayanamsa": "Lahiri"
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/events/verify-past",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "events", "verify-past"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "4. Shastriya Classical Rules Knowledge Base",
                "item": [
                    {
                        "name": "Get Total Classical Rules Count (12,578)",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwt_token}}"}],
                            "url": {
                                "raw": "{{base_url}}/api/v1/rules/count",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "rules", "count"]
                            }
                        }
                    },
                    {
                        "name": "Inverted Index Fast Rule Search",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwt_token}}"}],
                            "url": {
                                "raw": "{{base_url}}/api/v1/rules/search?planet=Jupiter&house=1&limit=10",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "rules", "search"],
                                "query": [
                                    {"key": "planet", "value": "Jupiter"},
                                    {"key": "house", "value": "1"},
                                    {"key": "limit", "value": "10"}
                                ]
                            }
                        }
                    }
                ]
            },
            {
                "name": "5. SaaS Billing & Monetization",
                "item": [
                    {
                        "name": "List Subscription Plans Catalog",
                        "request": {
                            "method": "GET",
                            "url": {
                                "raw": "{{base_url}}/api/v1/billing/plans",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "billing", "plans"]
                            }
                        }
                    },
                    {
                        "name": "Check Subscription Status",
                        "request": {
                            "method": "GET",
                            "header": [{"key": "Authorization", "value": "Bearer {{jwt_token}}"}],
                            "url": {
                                "raw": "{{base_url}}/api/v1/billing/status",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "billing", "status"]
                            }
                        }
                    },
                    {
                        "name": "Create Checkout Session (Stripe / Razorpay)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({"plan_id": "pro_monthly", "provider": "stripe"}, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/billing/checkout",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "billing", "checkout"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "6. Master Report Exports",
                "item": [
                    {
                        "name": "Generate Master Natal Kundali HTML Report",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "name": "Report Subject",
                                    "birth_date": "1995-05-15",
                                    "birth_time": "14:30:00",
                                    "latitude": 28.6139,
                                    "longitude": 77.2090,
                                    "timezone_offset": 5.5
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/reports/master-html",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "reports", "master-html"]
                            }
                        }
                    },
                    {
                        "name": "Generate Event Verification Certificate",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "verification_id": 1
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/reports/event-verification-certificate",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "reports", "event-verification-certificate"]
                            }
                        }
                    }
                ]
            },
            {
                "name": "7. Grounded AI Consultation",
                "item": [
                    {
                        "name": "Grounded Astrological Chat (Gemini 2.5 Flash)",
                        "request": {
                            "method": "POST",
                            "header": [
                                {"key": "Content-Type", "value": "application/json"},
                                {"key": "Authorization", "value": "Bearer {{jwt_token}}"}
                            ],
                            "body": {
                                "mode": "raw",
                                "raw": json.dumps({
                                    "query": "मेरी वर्तमान दशा और गोचर के अनुसार करियर में क्या बदलाव दिख रहे हैं?",
                                    "language": "Hindi",
                                    "birth_data": {
                                        "name": "Consult Native",
                                        "birth_date": "1995-05-15",
                                        "birth_time": "14:30:00",
                                        "latitude": 28.6139,
                                        "longitude": 77.2090,
                                        "timezone_offset": 5.5
                                    }
                                }, indent=2)
                            },
                            "url": {
                                "raw": "{{base_url}}/api/v1/chat/consult",
                                "host": ["{{base_url}}"],
                                "path": ["api", "v1", "chat", "consult"]
                            }
                        }
                    }
                ]
            }
        ]
    }

    out_file = Path("docs/Bharat_Jyotish_API_v1.postman_collection.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)
    print(f"Successfully created Postman collection: {out_file}")

if __name__ == "__main__":
    build_postman_collection()
