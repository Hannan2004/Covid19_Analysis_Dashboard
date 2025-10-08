# 🦠 COVID-19 Real-Time Dashboard

A comprehensive real-time COVID-19 data pipeline and visualization dashboard built with modern data engineering technologies. The system fetches live COVID-19 data, processes it through Apache Kafka, stores it in Neo4j graph database, and displays interactive visualizations via a Streamlit web application.

## 📊 Features

- **Real-time Data Streaming**: Automated data fetching from disease.sh API every 2 minutes
- **Interactive Dashboard**: Beautiful charts and country-wise analysis with Streamlit
- **Graph Database**: Efficient data storage and querying with Neo4j
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Event-Driven Architecture**: Apache Kafka for reliable message streaming
- **Dockerized Infrastructure**: Easy deployment with Docker Compose

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit, Plotly, Pandas |
| **Backend API** | FastAPI, Uvicorn |
| **Message Broker** | Apache Kafka |
| **Database** | Neo4j Graph Database |
| **Data Processing** | Python, Kafka-Python |
| **Infrastructure** | Docker, Docker Compose |
| **Environment** | Python Virtual Environment |


## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git

### 1. Clone Repository

```bash
git clone https://github.com/Hannan2004/Covid19_Analysis_Dashboard.git
cd Covid19_Analysis_Dashboard
```

### 2. Start Infrastructure
```bash
# Start Kafka, Zookeeper and Neo4j
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 3. Setup Python Environment
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 4. Run Services
### Terminal 1 - Data Producer:
```bash
cd backend
venv\Scripts\activate
python app/producer.py
```
### Terminal 2 - FastAPI Backend
```bash
cd dashboard
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3 - Streamlit Dashboard
```bash
cd backend
cd app
venv\Scripts\activate
streamlit run app.py
```

## 🌐 Access Points
| Service | URL | Description |
|-----------|------------|------------|
| **Dashboard** | http://localhost:8501 | Main Streamlit application |
| **API** | http://localhost:8000 | FastAPI backend |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Neo4j Browser** | http://localhost:7474  | Dashboard interface (neo4j/password123) |

## 📋 API Endpoints
```bash
GET /                    # Health check
GET /health             # Detailed system status
GET /countries          # All countries data
GET /countries/{name}   # Specific country data
GET /stats/global       # Global statistics
GET /stats/top/{limit}  # Top countries by cases
```

## 🔧 Configuration
```bash
Environment variables in dashboard/.env:
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASS=password123
API_BASE_URL=http://localhost:8000
```

## 🛑 Stopping Services
```bash
# Stop Python applications
Ctrl+C in each terminal

# Stop Docker services
docker-compose down

# Deactivate virtual environment
deactivate
```

## 🐛 Troubleshooting
### Services not starting:
```bash
# Check Docker services
docker-compose logs

# Restart services
docker-compose restart
```

### API connection issues:
```bash
# Test API health
curl http://localhost:8000/health

# Check Neo4j connection
docker-compose logs neo4j
```

### No data appearing:
```bash
# Verify producer is running and sending data
# Check producer terminal for "✅ Sent data for..." messages

# Verify Neo4j has data
# Open http://localhost:7474 and run: MATCH (c:Country) RETURN count(c)
```

## 📊 Dashboard Features
- Global Statistics: Total cases, deaths, recoveries, and active cases
- Country Rankings: Top countries by confirmed cases
- Visual Charts: Interactive bar charts and pie charts
- Country Analysis: Detailed individual country statistics
- System Monitoring: Real-time health check and API status
- Auto-refresh: Configurable dashboard updates
