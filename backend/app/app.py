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
    page_title="COVID-19 Real-Time Dashboard",
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
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=30)
def get_api_data(endpoint):
    """Fetch data from API with error handling and caching"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
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
        
        col1, col2 = st.columns(2)
        
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
            endpoints = ["/", "/countries", "/stats/global"]
            
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
    # Sidebar for navigation
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2659/2659980.png", width=80)
        st.title("🦠 COVID Dashboard")
        
        # Navigation menu
        page = st.selectbox(
            "Navigate to:",
            ["🏠 Main Dashboard", "📋 Countries Data", "🔍 Country Analysis", "⚙️ System Status"]
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
        st.info("Real-time data from disease.sh API")
        st.info("Updates every 2 minutes")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    # Route to different pages based on selection
    if page == "🏠 Main Dashboard":
        show_main_dashboard()
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
            <p>🦠 COVID-19 Real-Time Dashboard | Backend + Frontend in Virtual Environment</p>
            <p>Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>API Status: <a href="{API_BASE_URL}/health" target="_blank">Health Check</a></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()