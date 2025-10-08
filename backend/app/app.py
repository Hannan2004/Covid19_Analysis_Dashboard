import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="COVID-19 AI Analytics Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4b4b;
    }
    .stMetric > label {
        font-size: 14px !important;
        font-weight: bold !important;
    }
    .sidebar .stSelectbox > label {
        color: #262730;
        font-weight: bold;
    }
    .ai-insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
    }
    .trend-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .risk-high {
        border-left: 4px solid #dc3545;
        background-color: #f8d7da;
    }
    .risk-medium {
        border-left: 4px solid #ffc107;
        background-color: #fff3cd;
    }
    .risk-low {
        border-left: 4px solid #198754;
        background-color: #d1eddd;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def get_api_data(endpoint):
    """Fetch data from API with error handling and caching"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to fetch data from {endpoint}: {e}")
        return None

def show_main_dashboard():
    """Main dashboard view"""
    st.markdown('<h1 class="main-header">🦠 COVID-19 Real-Time Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")

    # Global Statistics
    st.subheader("🌍 Global COVID-19 Statistics")
    
    global_stats = get_api_data("/stats/global")
    if global_stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🦠 Total Confirmed", 
                f"{global_stats['total_confirmed']:,}",
                help="Total confirmed COVID-19 cases worldwide"
            )
        with col2:
            st.metric(
                "💀 Total Deaths", 
                f"{global_stats['total_deaths']:,}",
                help="Total deaths from COVID-19 worldwide"
            )
        with col3:
            st.metric(
                "✅ Total Recovered", 
                f"{global_stats['total_recovered']:,}",
                help="Total recovered from COVID-19 worldwide"
            )
        with col4:
            st.metric(
                "🚨 Active Cases", 
                f"{global_stats['active_cases']:,}",
                help="Currently active COVID-19 cases"
            )
    else:
        st.error("❌ Unable to fetch global statistics")

    st.markdown("---")

    # Charts Section
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Top Countries by Confirmed Cases")
        top_countries = get_api_data("/stats/top/15")
        
        if top_countries and len(top_countries) > 0:
            df_top = pd.DataFrame(top_countries)
            
            # Create horizontal bar chart
            fig_bar = px.bar(
                df_top, 
                x='confirmed', 
                y='country',
                orientation='h',
                title="Top 15 Countries - Confirmed Cases",
                color='confirmed',
                color_continuous_scale='Reds',
                labels={'confirmed': 'Confirmed Cases', 'country': 'Country'}
            )
            fig_bar.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=500,
                showlegend=False,
                font=dict(size=12)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("⚠️ No data available for top countries chart")

    with col_right:
        st.subheader("🎯 Case Distribution - Top 10")
        
        if top_countries and len(top_countries) >= 10:
            df_top = pd.DataFrame(top_countries)
            
            # Create pie chart for top 10
            fig_pie = px.pie(
                df_top.head(10), 
                values='confirmed', 
                names='country',
                title="Distribution of Cases - Top 10 Countries"
            )
            fig_pie.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                textfont_size=10
            )
            fig_pie.update_layout(
                height=500,
                font=dict(size=12)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("⚠️ Insufficient data for pie chart")

def show_ai_trend_analysis():
    """AI-Powered Trend Analysis Dashboard"""
    st.markdown('<h1 class="main-header">🤖 AI-Powered COVID-19 Trend Analysis</h1>', unsafe_allow_html=True)
    st.write("Intelligent analysis of COVID-19 patterns, anomalies, and predictions using AI.")
    
    # Sidebar for analysis options
    with st.sidebar:
        st.header("🔍 Analysis Options")
        analysis_type = st.selectbox(
            "Choose Analysis Type:",
            ["🌍 Global Trends", "🏳️ Country Analysis", "⚠️ Risk Assessment"]
        )
    
    if analysis_type == "🌍 Global Trends":
        render_global_trends()
    elif analysis_type == "🏳️ Country Analysis":
        render_country_analysis()
    elif analysis_type == "⚠️ Risk Assessment":
        render_risk_assessment()

def render_global_trends():
    """Render global trends analysis"""
    st.subheader("🌍 Global AI Trend Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Generate Global Analysis", type="primary", use_container_width=True):
            st.session_state.analyze_global = True
    
    with col1:
        st.write("Click the button to generate comprehensive AI analysis of global COVID-19 trends.")
    
    if st.session_state.get('analyze_global', False):
        with st.spinner("🤖 AI is analyzing global COVID-19 trends... This may take a moment."):
            try:
                response = get_api_data("/trends/global")
                
                if response and response.get("status") == "success":
                    data = response.get("data", {})
                    
                    # AI Analysis Section
                    st.markdown('<div class="ai-insight-box">', unsafe_allow_html=True)
                    st.markdown("## 🧠 AI-Generated Insights")
                    ai_analysis = data.get("ai_analysis", "No analysis available")
                    st.markdown(ai_analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Global Statistics Overview
                    st.subheader("📊 Global Statistics Overview")
                    stats = data.get("global_stats", {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Cases", f"{stats.get('total_confirmed', 0):,}")
                    with col2:
                        st.metric("Total Deaths", f"{stats.get('total_deaths', 0):,}")
                    with col3:
                        st.metric("Active Cases", f"{stats.get('active_cases', 0):,}")
                    with col4:
                        st.metric("Global Death Rate", f"{stats.get('global_death_rate', 0):.2f}%")
                    
                    # Trend Indicators
                    st.subheader("📈 Trend Indicators")
                    trends = data.get("trends", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown('<div class="trend-card">', unsafe_allow_html=True)
                        st.metric("Avg Death Rate (Top 20)", f"{trends.get('avg_death_rate', 0):.2f}%")
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="trend-card">', unsafe_allow_html=True)
                        st.metric("High Death Rate Countries", trends.get('high_death_rate_countries', 0))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="trend-card">', unsafe_allow_html=True)
                        st.metric("Low Recovery Countries", trends.get('low_recovery_rate_countries', 0))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Anomalies Detection
                    st.subheader("🚨 Detected Anomalies")
                    anomalies = data.get("anomalies", {})
                    
                    if anomalies.get('countries_with_unusual_death_rates'):
                        st.warning(f"**⚠️ Unusual Death Rates:** {', '.join(anomalies['countries_with_unusual_death_rates'][:5])}")
                    
                    if anomalies.get('countries_with_unusual_recovery_rates'):
                        st.warning(f"**⚠️ Unusual Recovery Rates:** {', '.join(anomalies['countries_with_unusual_recovery_rates'][:5])}")
                    
                    # Top Countries Visualization
                    if data.get("top_countries"):
                        st.subheader("📊 Top Countries Analysis")
                        df = pd.DataFrame(data["top_countries"])
                        
                        # Death Rate vs Cases Chart
                        fig = px.scatter(
                            df.head(15), 
                            x="confirmed", 
                            y="death_rate",
                            size="active",
                            color="recovery_rate",
                            hover_name="country",
                            title="Death Rate vs Confirmed Cases (Top 15 Countries)",
                            labels={
                                "confirmed": "Confirmed Cases",
                                "death_rate": "Death Rate (%)",
                                "recovery_rate": "Recovery Rate (%)"
                            },
                            color_continuous_scale="RdYlGn"
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Recovery Rate Comparison
                        fig2 = px.bar(
                            df.head(10), 
                            x="country", 
                            y="recovery_rate",
                            title="Recovery Rates - Top 10 Countries",
                            color="recovery_rate",
                            color_continuous_scale="Greens"
                        )
                        fig2.update_xaxes(tickangle=45)
                        fig2.update_layout(height=400)
                        st.plotly_chart(fig2, use_container_width=True)
                
                else:
                    st.error("❌ Failed to get global trends analysis")
                    
            except Exception as e:
                st.error(f"❌ Error getting global trends: {str(e)}")
        
        # Reset the state
        st.session_state.analyze_global = False

def render_country_analysis():
    """Render country-specific analysis"""
    st.subheader("🏳️ Country-Specific AI Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        country = st.text_input("🔍 Enter country name:", placeholder="e.g., United States, India, Germany")
    
    with col2:
        analyze_button = st.button("🔍 Analyze Country", type="primary", use_container_width=True)
    
    if analyze_button and country:
        with st.spinner(f"🤖 AI is analyzing COVID-19 trends for {country}..."):
            try:
                response = get_api_data(f"/trends/country/{country}")
                
                if response and response.get("status") == "success":
                    data = response.get("data", {})
                    
                    # AI Analysis
                    st.markdown('<div class="ai-insight-box">', unsafe_allow_html=True)
                    st.markdown(f"## 🧠 AI Analysis for {data.get('country', country)}")
                    ai_analysis = data.get("ai_analysis", "No analysis available")
                    st.markdown(ai_analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Current Statistics
                    st.subheader("📊 Current Statistics")
                    stats = data.get("current_stats", {})
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Confirmed Cases", f"{stats.get('confirmed', 0):,}")
                        st.metric("Deaths", f"{stats.get('deaths', 0):,}")
                    with col2:
                        st.metric("Recovered", f"{stats.get('recovered', 0):,}")
                        st.metric("Active Cases", f"{stats.get('active', 0):,}")
                    with col3:
                        st.metric("Death Rate", f"{stats.get('death_rate', 0):.2f}%")
                        st.metric("Recovery Rate", f"{stats.get('recovery_rate', 0):.2f}%")
                    
                    # Global Comparison
                    st.subheader("🌍 Comparison with Global Averages")
                    trends = data.get("trends", {})
                    global_stats = data.get("global_context", {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        death_diff = trends.get("death_rate_vs_global", 0)
                        st.metric(
                            "Death Rate vs Global", 
                            f"{death_diff:+.2f}%",
                            delta=f"Global: {global_stats.get('global_death_rate', 0):.2f}%"
                        )
                    with col2:
                        recovery_diff = trends.get("recovery_rate_vs_global", 0)
                        st.metric(
                            "Recovery Rate vs Global", 
                            f"{recovery_diff:+.2f}%",
                            delta=f"Global: {global_stats.get('global_recovery_rate', 0):.2f}%"
                        )
                    
                    # Case Distribution Visualization
                    st.subheader("📊 Case Distribution")
                    
                    # Create donut chart for case distribution
                    labels = ['Active', 'Recovered', 'Deaths']
                    values = [stats.get('active', 0), stats.get('recovered', 0), stats.get('deaths', 0)]
                    colors = ['orange', 'green', 'red']
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=labels, 
                        values=values,
                        hole=0.4,
                        marker_colors=colors
                    )])
                    
                    fig.update_layout(
                        title=f"Case Distribution - {country}",
                        height=400,
                        annotations=[dict(text=country, x=0.5, y=0.5, font_size=20, showarrow=False)]
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                elif response and response.get("status") == "error":
                    st.error(f"❌ Country '{country}' not found. Please check the spelling.")
                else:
                    st.error("❌ Failed to analyze country")
                    
            except Exception as e:
                st.error(f"❌ Error analyzing country: {str(e)}")

def render_risk_assessment():
    """Render risk assessment dashboard"""
    st.subheader("⚠️ Global Risk Assessment")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Generate Risk Assessment", type="primary", use_container_width=True):
            st.session_state.analyze_risk = True
    
    with col1:
        st.write("AI-powered risk assessment calculating threat levels for all countries.")
    
    if st.session_state.get('analyze_risk', False):
        with st.spinner("🤖 AI is calculating risk scores for all countries..."):
            try:
                response = get_api_data("/trends/risk-assessment")
                
                if response and response.get("status") == "success":
                    data = response.get("data", {})
                    
                    # AI Risk Analysis
                    st.markdown('<div class="ai-insight-box">', unsafe_allow_html=True)
                    st.markdown("## 🧠 AI Risk Analysis")
                    ai_analysis = data.get("ai_analysis", "No analysis available")
                    st.markdown(ai_analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Risk Distribution
                    high_risk = data.get("high_risk_countries", [])
                    medium_risk = data.get("medium_risk_countries", [])
                    low_risk = data.get("low_risk_countries", [])
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown('<div class="trend-card risk-high">', unsafe_allow_html=True)
                        st.metric("🔴 High Risk", len(high_risk))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown('<div class="trend-card risk-medium">', unsafe_allow_html=True)
                        st.metric("🟡 Medium Risk", len(medium_risk))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col3:
                        st.markdown('<div class="trend-card risk-low">', unsafe_allow_html=True)
                        st.metric("🟢 Low Risk", len(low_risk))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # High Risk Countries Details
                    if high_risk:
                        st.subheader("🔴 High Risk Countries")
                        
                        # Risk Score Chart
                        risk_df = pd.DataFrame(high_risk[:15])
                        
                        fig = px.bar(
                            risk_df,
                            x="country",
                            y="risk_score",
                            title="Risk Scores - Top 15 Highest Risk Countries",
                            color="death_rate",
                            color_continuous_scale="Reds",
                            hover_data=["confirmed", "deaths", "active"]
                        )
                        fig.update_xaxes(tickangle=45)
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Risk vs Cases Scatter Plot
                        fig2 = px.scatter(
                            risk_df,
                            x="confirmed",
                            y="risk_score",
                            size="active",
                            color="death_rate",
                            hover_name="country",
                            title="Risk Score vs Confirmed Cases",
                            labels={
                                "confirmed": "Confirmed Cases",
                                "risk_score": "Risk Score",
                                "death_rate": "Death Rate (%)"
                            },
                            color_continuous_scale="Reds"
                        )
                        fig2.update_layout(height=400)
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        # Detailed Risk Table
                        st.subheader("📊 Detailed Risk Assessment")
                        
                        # Format the dataframe for display
                        display_df = risk_df[["country", "confirmed", "deaths", "death_rate", "recovery_rate", "risk_score"]].copy()
                        display_df["confirmed"] = display_df["confirmed"].apply(lambda x: f"{x:,}")
                        display_df["deaths"] = display_df["deaths"].apply(lambda x: f"{x:,}")
                        display_df["death_rate"] = display_df["death_rate"].round(2)
                        display_df["recovery_rate"] = display_df["recovery_rate"].round(2)
                        display_df["risk_score"] = display_df["risk_score"].round(1)
                        
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            column_config={
                                "country": "Country",
                                "confirmed": "Cases",
                                "deaths": "Deaths",
                                "death_rate": "Death Rate (%)",
                                "recovery_rate": "Recovery Rate (%)",
                                "risk_score": "Risk Score"
                            }
                        )
                
                else:
                    st.error("❌ Failed to get risk assessment")
                    
            except Exception as e:
                st.error(f"❌ Error getting risk assessment: {str(e)}")
        
        # Reset the state
        st.session_state.analyze_risk = False

def show_countries_table():
    """Countries data table view"""
    st.subheader("📋 All Countries COVID-19 Data")
    
    countries_data = get_api_data("/countries")
    if countries_data and len(countries_data) > 0:
        df_countries = pd.DataFrame(countries_data)
        
        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_country = st.text_input("🔍 Search for a country:")
        
        with col2:
            sort_by = st.selectbox(
                "Sort by:", 
                options=['confirmed', 'deaths', 'recovered'],
                index=0
            )
        
        with col3:
            st.metric("Total Countries", len(df_countries))
        
        # Filter data based on search
        if search_country:
            df_filtered = df_countries[
                df_countries['country'].str.contains(search_country, case=False, na=False)
            ]
        else:
            df_filtered = df_countries
        
        # Sort data
        if not df_filtered.empty:
            df_sorted = df_filtered.sort_values(by=sort_by, ascending=False)
            
            st.write(f"**Showing {len(df_sorted)} countries**")
            
            # Format the dataframe for better display
            df_display = df_sorted.copy()
            df_display['confirmed'] = df_display['confirmed'].apply(lambda x: f"{x:,}")
            df_display['deaths'] = df_display['deaths'].apply(lambda x: f"{x:,}")
            df_display['recovered'] = df_display['recovered'].apply(lambda x: f"{x:,}")
            
            # Display the table
            st.dataframe(
                df_display,
                use_container_width=True,
                height=400
            )
        else:
            st.info("🔍 No countries found matching your search criteria.")
    else:
        st.error("❌ Unable to fetch countries data")

def show_individual_country():
    """Individual country analysis view"""
    st.subheader("🔍 Individual Country Analysis")
    
    countries_data = get_api_data("/countries")
    if countries_data and len(countries_data) > 0:
        # Create sorted list of country names
        country_names = sorted([country['country'] for country in countries_data])
        
        selected_country = st.selectbox("Select a country to analyze:", options=country_names)
        
        if selected_country:
            country_detail = get_api_data(f"/countries/{selected_country}")
            
            if country_detail:
                # Main metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🦠 Confirmed Cases", f"{country_detail['confirmed']:,}")
                with col2:
                    st.metric("💀 Deaths", f"{country_detail['deaths']:,}")
                with col3:
                    st.metric("✅ Recovered", f"{country_detail['recovered']:,}")
                
                # Calculate additional metrics
                confirmed = country_detail['confirmed']
                deaths = country_detail['deaths']
                recovered = country_detail['recovered']
                active = confirmed - deaths - recovered
                
                st.markdown("---")
                
                # Additional calculated metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🚨 Active Cases", f"{active:,}")
                
                with col2:
                    if confirmed > 0:
                        mortality_rate = (deaths / confirmed * 100)
                        st.metric("💀 Mortality Rate", f"{mortality_rate:.2f}%")
                    else:
                        st.metric("💀 Mortality Rate", "0.00%")
                
                with col3:
                    if confirmed > 0:
                        recovery_rate = (recovered / confirmed * 100)
                        st.metric("✅ Recovery Rate", f"{recovery_rate:.2f}%")
                    else:
                        st.metric("✅ Recovery Rate", "0.00%")
                
                # Visualization
                st.markdown("---")
                st.subheader(f"📊 Case Distribution for {selected_country}")
                
                # Create stacked bar chart
                fig = go.Figure(data=[
                    go.Bar(name='Active', x=[selected_country], y=[active], marker_color='orange'),
                    go.Bar(name='Recovered', x=[selected_country], y=[recovered], marker_color='green'),
                    go.Bar(name='Deaths', x=[selected_country], y=[deaths], marker_color='red')
                ])
                
                fig.update_layout(
                    barmode='stack',
                    height=400,
                    title=f"COVID-19 Case Breakdown - {selected_country}",
                    yaxis_title="Number of Cases",
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"❌ Unable to fetch detailed data for {selected_country}")
    else:
        st.error("❌ Unable to fetch countries list")

def show_api_status():
    """API status and system health view"""
    st.subheader("📊 System Status & Health Check")
    
    # API Health Check
    health_data = get_api_data("/health")
    
    if health_data:
        status = health_data.get("status", "unknown")
        
        # Display overall status
        if status == "healthy":
            st.success(f"✅ **System Status:** {status.upper()}")
        else:
            st.warning(f"⚠️ **System Status:** {status.upper()}")
        
        # Services status
        st.markdown("### 🔧 Service Status")
        services = health_data.get("services", {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            neo4j_status = services.get("neo4j", "unknown")
            if neo4j_status == "connected":
                st.success(f"✅ **Neo4j Database:** {neo4j_status}")
            else:
                st.error(f"❌ **Neo4j Database:** {neo4j_status}")
        
        with col2:
            api_status = services.get("api", "unknown")
            if api_status == "running":
                st.success(f"✅ **FastAPI Service:** {api_status}")
            else:
                st.error(f"❌ **FastAPI Service:** {api_status}")
        
        with col3:
            groq_status = services.get("groq", "unknown")
            if groq_status == "connected":
                st.success(f"✅ **Groq AI:** {groq_status}")
            elif groq_status == "disconnected":
                st.warning(f"⚠️ **Groq AI:** {groq_status}")
            else:
                st.error(f"❌ **Groq AI:** {groq_status}")
        
        # Trend Analysis Service Check
        st.markdown("### 🤖 AI Services Status")
        trend_health = get_api_data("/trends/health")
        
        if trend_health:
            if trend_health.get("status") == "healthy":
                st.success("✅ **AI Trend Analysis:** Operational")
            else:
                st.error("❌ **AI Trend Analysis:** Error")
        else:
            st.warning("⚠️ **AI Trend Analysis:** Service unavailable")
        
        # System information
        st.markdown("### ℹ️ System Information")
        
        info_col1, info_col2 = st.columns(2)
        
        with info_col1:
            st.info(f"**API Endpoint:** {API_BASE_URL}")
            st.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with info_col2:
            if 'timestamp' in health_data:
                st.info(f"**Server Time:** {health_data['timestamp']}")
            
            # Test all endpoints
            st.markdown("**🔗 Endpoint Tests:**")
            endpoints = ["/", "/countries", "/stats/global", "/trends/health"]
            
            for endpoint in endpoints:
                try:
                    test_response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
                    if test_response.status_code == 200:
                        st.text(f"✅ {endpoint}")
                    else:
                        st.text(f"❌ {endpoint} ({test_response.status_code})")
                except:
                    st.text(f"❌ {endpoint} (timeout)")
        
        # Raw health data
        with st.expander("🔍 Raw Health Check Response"):
            st.json(health_data)
    else:
        st.error("❌ **API Unavailable** - Cannot connect to backend service")
        st.info(f"Trying to connect to: {API_BASE_URL}")

def main():
    # Initialize session state
    if 'analyze_global' not in st.session_state:
        st.session_state.analyze_global = False
    if 'analyze_risk' not in st.session_state:
        st.session_state.analyze_risk = False
    
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2659/2659980.png", width=80)
        st.title("🦠 COVID AI Dashboard")
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            [
                "🏠 Main Dashboard", 
                "🤖 AI Trend Analysis",
                "📋 Countries Data", 
                "🔍 Country Analysis", 
                "⚙️ System Status"
            ]
        )
        
        st.markdown("---")
        
        # Control panel
        st.markdown("### ⚙️ Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh (30s)", value=False)
        
        # Manual refresh button
        if st.button("🔄 Refresh Now", type="primary"):
            st.cache_data.clear()
            st.rerun()
        
        # Data source info
        st.markdown("---")
        st.markdown("### 📡 Data Source")
        st.info("Real-time data from internal API")
        st.info("AI Analysis powered by Groq")
        st.info("Updates every 30 seconds")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Route to different pages based on selection
    if page == "🏠 Main Dashboard":
        show_main_dashboard()
    elif page == "🤖 AI Trend Analysis":
        show_ai_trend_analysis()
    elif page == "📋 Countries Data":
        show_countries_table()
    elif page == "🔍 Country Analysis":
        show_individual_country()
    elif page == "⚙️ System Status":
        show_api_status()
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; font-size: 12px;'>
            <p>🦠 COVID-19 AI Analytics Dashboard | Powered by FastAPI + Neo4j + Groq</p>
            <p>Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>API Status: <a href="{API_BASE_URL}/health" target="_blank">Health Check</a> | 
            AI Status: <a href="{API_BASE_URL}/trends/health" target="_blank">Trend Health</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()