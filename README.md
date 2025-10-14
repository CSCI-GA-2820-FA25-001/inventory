# 🏪 NYU DevOps Project — Inventory Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Tests](https://img.shields.io/badge/Coverage-95%25%2B-brightgreen.svg)](https://pytest.org/)

A RESTful microservice for managing **product inventory** for an eCommerce platform, developed by the **Inventory Squad** for NYU’s **CSCI-GA-2820-001 DevOps and Agile Methodologies (Fall 2025)**.

---

## 📘 Overview

The **Inventory Service** keeps track of how many units of each product exist in the warehouse, their condition, and restock levels.
It supports full **CRUD + LIST** operations and returns JSON-only responses, following RESTful conventions and **Test-Driven Development (TDD)** practices with **95%+ code coverage**.

---

## 🧩 Features

* **Create** a new inventory record
* **Read** details of a single product’s inventory
* **Update** product quantity, restock level, or restock amount
* **Delete** an inventory record (endpoint not implemented yet)
* **List** all inventory items
* Query by condition (`NEW`, `USED`, `OPEN_BOX`)
* Health check via root `/` route

---

## 🧱 Technology Stack

* **Python 3.11+**
* **Flask** — Web micro-framework
* **PostgreSQL** — Database
* **SQLAlchemy** — ORM for persistence
* **pytest / pytest-cov** — Testing & coverage
* **Docker + VSCode Dev Containers** — Local environment

---

## ⚙️ Setup and Installation

### Prerequisites

* Docker Desktop
* Visual Studio Code (with Remote Containers extension)

### Steps

```bash
# Clone this repository
git clone https://github.com/nyu-devops-fa25/inventory.git
cd inventory

# Open in VSCode and choose "Reopen in Container"
code .

# Wait for the container to finish building
```

### Initialize Database

```bash
flask run
```

The service starts at **[http://localhost:8080/](http://localhost:8080/)**

---

## 🧾 Data Model

| Field            | Type    | Description                                   |
| ---------------- | ------- | --------------------------------------------- |
| `id`             | Integer | Auto-generated unique identifier              |
| `product_id`     | Integer | Product ID                                    |
| `quantity`       | Integer | Current quantity in stock                     |
| `restock_level`  | Integer | Threshold for reordering                      |
| `restock_amount` | Integer | Amount to restock when threshold is reached   |
| `condition`      | String  | Condition of item (`NEW`, `USED`, `OPEN_BOX`) |

---

## 🌐 REST API Endpoints

**Base URL:** `http://localhost:8080`

### Root — `GET /`

Returns a plain text reminder message.

```
Reminder: return some useful information in json format about the service here
```

**Response 200**

---

### 1. List All Inventory Items — `GET /inventory`

**Response 200**

```json
[
  {
    "id": 1,
    "product_id": 1001,
    "quantity": 25,
    "restock_level": 10,
    "restock_amount": 5,
    "condition": "NEW"
  },
  {
    "id": 2,
    "product_id": 1002,
    "quantity": 5,
    "restock_level": 20,
    "restock_amount": 10,
    "condition": "USED"
  }
]
```

---

### 2. Create Inventory Record — `POST /inventory`

**Request**

```json
{
  "product_id": 3005,
  "quantity": 40,
  "restock_level": 10,
  "restock_amount": 5,
  "condition": "OPEN_BOX"
}
```

**Response 201**

```json
{
  "id": 3,
  "product_id": 3005,
  "quantity": 40,
  "restock_level": 10,
  "restock_amount": 5,
  "condition": "OPEN_BOX"
}
```

*Includes `Location` header with URL of the newly created resource.*

---

### 3. Retrieve One Record — `GET /inventory/<id>`

**Response 200**

```json
{
  "id": 3,
  "product_id": 3005,
  "quantity": 40,
  "restock_level": 10,
  "restock_amount": 5,
  "condition": "OPEN_BOX"
}
```

Error: `404 Not Found` — when record doesn’t exist.

---

### 4. Update Record — `PUT /inventory/<id>`

**Request**

```json
{
  "quantity": 60,
  "restock_level": 15,
  "restock_amount": 10,
  "condition": "OPEN_BOX"
}
```

**Response 200**

```json
{
  "id": 3,
  "product_id": 3005,
  "quantity": 60,
  "restock_level": 15,
  "restock_amount": 10,
  "condition": "OPEN_BOX"
}
```

---

### 5. Delete Record — `DELETE /inventory/<id>`

**Response 204 No Content**

Error: `404 Not Found` — when record doesn’t exist.

---

## ⚡ Example CURL Commands

```bash
# Root
curl http://localhost:8080/

# List all
curl http://localhost:8080/inventory

# Get one
curl http://localhost:8080/inventory/1

# Create
curl -X POST http://localhost:8080/inventory \
     -H "Content-Type: application/json" \
     -d '{"product_id":3005,"quantity":40,"restock_level":10,"restock_amount":5,"condition":"OPEN_BOX"}'

# Update
curl -X PUT http://localhost:8080/inventory/1 \
     -H "Content-Type: application/json" \
     -d '{"quantity":60,"restock_level":15,"restock_amount":10,"condition":"OPEN_BOX"}'

# Delete
curl -X DELETE http://localhost:8080/inventory/1
```

---

## 📊 HTTP Status Codes

| Code                         | Meaning                             | Used When                 |
| ---------------------------- | ----------------------------------- | ------------------------- |
| `200 OK`                     | Successful GET or PUT               | Resource found or updated |
| `201 Created`                | Successful POST                     | Resource created          |
| `204 No Content`             | Successful DELETE                   | Resource removed          |
| `400 Bad Request`            | Invalid or missing JSON             | Bad input                 |
| `404 Not Found`              | Resource doesn’t exist              | Wrong ID                  |
| `405 Method Not Allowed`     | Unsupported HTTP verb               | e.g. `PUT /inventory`     |
| `415 Unsupported Media Type` | Content-Type not `application/json` |                           |
| `500 Internal Server Error`  | Unexpected server error             |                           |

---

## 🧪 Testing & Quality

All code follows **TDD** with pytest.
Write tests first → implement code → ensure all green.

```bash
# Run all tests
make test

# Run coverage
pytest --cov=service --cov-report term-missing

# Lint for PEP8 compliance
make lint
```

✅ Coverage goal: **≥ 95%**
✅ Pylint score: **≥ 9.0/10**

---

## 🔄 Development Workflow

* Use **GitHub branches** for each story
* Create **Pull Requests (PRs)** — connect them to ZenHub issues
* Move stories across columns (`To Do → In Progress → Review/QA → Done`)
* Use **burndown chart** for sprint tracking
* Code merges only via approved PRs

---

## 🧰 Project Structure

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── factories.py           - Factory for testing with fake objects
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

---

## 🪪 License

Copyright (c) 2016, 2025 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
