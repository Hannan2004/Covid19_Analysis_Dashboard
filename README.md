# 🦠 COVID-19 AI-Powered Real-Time Dashboard

A comprehensive real-time COVID-19 data pipeline and visualization dashboard built with modern data engineering technologies and AI-powered analytics. The system fetches live COVID-19 data, processes it through Apache Kafka, stores it in Neo4j graph database, performs intelligent trend analysis using Groq AI, and displays interactive visualizations via a Streamlit web application.

## 📊 Features

- **Real-time Data Streaming**: Automated data fetching from disease.sh API every 2 minutes
- **🤖 AI-Powered Trend Analysis**: Intelligent COVID-19 pattern recognition and predictions using Groq AI
- **Interactive Dashboard**: Beautiful charts and country-wise analysis with Streamlit
- **Graph Database**: Efficient data storage and querying with Neo4j
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Event-Driven Architecture**: Apache Kafka for reliable message streaming
- **Dockerized Infrastructure**: Easy deployment with Docker Compose
- **🧠 Smart Analytics**: Anomaly detection, risk assessment, and predictive insights
- **📈 Advanced Visualizations**: Trend charts, risk heatmaps, and correlation analysis

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit, Plotly, Pandas |
| **Backend API** | FastAPI, Uvicorn |
| **AI/ML** | Groq AI, LangChain, NumPy |
| **Message Broker** | Apache Kafka |
| **Database** | Neo4j Graph Database |
| **Data Processing** | Python, Kafka-Python |
| **Infrastructure** | Docker, Docker Compose |
| **Environment** | Python Virtual Environment |

## 🤖 AI Features

### Global Trend Analysis
- **Pattern Recognition**: Identifies global COVID-19 trends and patterns
- **Anomaly Detection**: Detects unusual death rates and recovery patterns
- **Statistical Analysis**: Advanced metrics like IQR outlier detection
- **AI Insights**: Natural language explanations of complex data patterns

### Country-Specific Analysis
- **Comparative Analysis**: Compares individual countries against global averages
- **Trend Interpretation**: AI-powered analysis of country-specific trends
- **Risk Factors**: Identifies key risk indicators for each country
- **Personalized Recommendations**: Country-specific suggestions and insights

### Risk Assessment
- **Automated Risk Scoring**: Calculates risk scores based on multiple factors
- **Risk Categorization**: Classifies countries into high/medium/low risk categories
- **Priority Alerts**: Highlights countries requiring immediate attention
- **Predictive Analytics**: Forecasts potential outbreak scenarios

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Docker & Docker Compose
- Git
- **Groq API Key** (Get from [console.groq.com](https://console.groq.com))

### 1. Clone Repository

```bash
git clone https://github.com/Hannan2004/Covid19_Analysis_Dashboard.git
cd Covid19_Analysis_Dashboard
```

### 2. Setup Environment Variables
```bash
cd backend

# Create .env file with your Groq API key
echo "KAFKA_BOOTSTRAP_SERVERS=localhost:9092" > .env
echo "NEO4J_URI=bolt://localhost:7687" >> .env
echo "NEO4J_USER=neo4j" >> .env
echo "NEO4J_PASS=password123" >> .env
echo "API_BASE_URL=http://localhost:8000" >> .env
echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
```

### 3. Start Infrastructure
```bash
# Start Kafka, Zookeeper and Neo4j
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 4. Setup Python Environment
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies (including AI packages)
pip install -r requirements.txt
```

### 5. Run Services
### Terminal 1 - Data Producer:
```bash
cd backend
venv\Scripts\activate
python app/producer.py
```
### Terminal 2 - FastAPI Backend (with AI endpoints)
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 3 - Streamlit Dashboard (with AI features)
```bash
cd backend/app
venv\Scripts\activate
streamlit run app.py
```

## 🌐 Access Points
| Service | URL | Description |
|-----------|------------|------------|
| **🏠 Main Dashboard** | http://localhost:8501 | Streamlit app with AI analytics |
| **🤖 AI Trend Analysis** | http://localhost:8501 | AI-powered trend analysis page |
| **API Backend** | http://localhost:8000 | FastAPI backend with AI endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Neo4j Browser** | http://localhost:7474  | Database interface (neo4j/password123) |

## 📋 API Endpoints

### Standard Endpoints
```bash
GET /                    # Health check
GET /health             # Detailed system status
GET /countries          # All countries data
GET /countries/{name}   # Specific country data
GET /stats/global       # Global statistics
GET /stats/top/{limit}  # Top countries by cases
```

### 🤖 AI Trend Analysis Endpoints
```bash
GET /trends/global           # Global AI trend analysis
GET /trends/country/{name}   # Country-specific AI analysis
GET /trends/risk-assessment  # AI-powered risk assessment
GET /trends/health          # AI service health check
```

## 🔧 Configuration
```bash
Environment variables in backend/.env:
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASS=password123
API_BASE_URL=http://localhost:8000
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

## 🧠 AI Dashboard Usage

### 1. Global Trends Analysis
1. Navigate to "🤖 AI Trend Analysis" in the sidebar
2. Select "🌍 Global Trends"
3. Click "🔄 Generate Global Analysis" 
4. View AI-generated insights, anomaly detection, and trend visualizations

### 2. Country Analysis
1. Select "🏳️ Country Analysis"
2. Enter a country name (e.g., "United States", "India")
3. Click "🔍 Analyze Country"
4. Get AI-powered comparative analysis and recommendations

### 3. Risk Assessment
1. Select "⚠️ Risk Assessment"
2. Click "🔄 Generate Risk Assessment"
3. View automated risk scoring and categorization
4. Identify high-priority countries requiring attention

## 📊 Dashboard Features

### Standard Features
- **Global Statistics**: Total cases, deaths, recoveries, and active cases
- **Country Rankings**: Top countries by confirmed cases
- **Visual Charts**: Interactive bar charts and pie charts
- **Country Analysis**: Detailed individual country statistics
- **System Monitoring**: Real-time health check and API status
- **Auto-refresh**: Configurable dashboard updates

### 🤖 AI-Enhanced Features
- **Intelligent Insights**: Natural language analysis of complex data patterns
- **Anomaly Alerts**: Automatic detection of unusual trends
- **Risk Visualization**: Color-coded risk assessment charts
- **Predictive Analytics**: AI-powered forecasting and trend predictions
- **Comparative Analysis**: Smart country-to-country and country-to-global comparisons
- **Interactive AI Chat**: Ask questions about COVID-19 trends and get AI responses

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

# Test AI endpoints
curl http://localhost:8000/trends/health

# Check Neo4j connection
docker-compose logs neo4j
```

### AI Analysis not working:
```bash
# Verify Groq API key in .env file
cat backend/.env | grep GROQ_API_KEY

# Check AI service health
curl http://localhost:8000/trends/health

# Verify Python AI packages installed
pip list | grep -E "(langchain|groq|numpy|pandas)"
```

### No data appearing:
```bash
# Verify producer is running and sending data
# Check producer terminal for "✅ Sent data for..." messages

# Verify Neo4j has data
# Open http://localhost:7474 and run: MATCH (c:Country) RETURN count(c)
```

## 🔍 Sample AI Outputs

### Global Trend Analysis
```
🧠 AI-Generated Insights:
The current global COVID-19 situation shows a death rate of 1.02% with significant 
regional variations. Countries like Yemen (18.1%) and Sudan (7.5%) show concerning 
death rates, while others maintain rates below 1%. The recovery rate stands at 97.8% 
globally, indicating effective treatment protocols...
```

### Risk Assessment
```
🔴 High Risk Countries (15):
- Yemen: 2,149 cases, 18.1% death rate, Risk Score: 89
- Sudan: 63,993 cases, 7.5% death rate, Risk Score: 85
- Syria: 57,423 cases, 5.5% death rate, Risk Score: 78
```