import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import PromptTemplate
from .groq_client import get_groq_llm
from .neo4j_client import driver
import json

class CovidTrendAnalyzer:
    def __init__(self):
        self.llm = get_groq_llm()
        self.driver = driver
        
        # Analysis prompt templates
        self.trend_analysis_prompt = PromptTemplate(
            input_variables=["data_summary", "trends", "anomalies"],
            template="""
You are an expert COVID-19 data analyst. Analyze the following data and provide insights:

DATA SUMMARY:
{data_summary}

DETECTED TRENDS:
{trends}

DETECTED ANOMALIES:
{anomalies}

Please provide:
1. **Key Insights**: What are the most important findings?
2. **Trend Interpretation**: What do these trends suggest about the pandemic situation?
3. **Risk Assessment**: Which countries or regions need attention?
4. **Recommendations**: What actions should be considered?
5. **Predictions**: Based on current trends, what might happen in the next 2-4 weeks?

Be specific, data-driven, and provide actionable insights. Use percentages and numbers from the data.
"""
        )
        
        self.country_analysis_prompt = PromptTemplate(
            input_variables=["country", "current_stats", "trend_data", "global_context"],
            template="""
Analyze COVID-19 trends for {country}:

CURRENT STATISTICS:
{current_stats}

TREND DATA:
{trend_data}

GLOBAL CONTEXT:
{global_context}

Provide detailed analysis:
1. **Current Situation**: How is {country} performing compared to global averages?
2. **Trend Analysis**: Are cases rising, falling, or stabilizing?
3. **Comparative Analysis**: How does {country} compare to similar countries?
4. **Risk Factors**: What are the main concerns?
5. **Recommendations**: Specific suggestions for {country}
"""
        )
    
    def _convert_numpy_types(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        return obj
    
    def get_global_trends(self) -> Dict[str, Any]:
        """Analyze global COVID-19 trends"""
        try:
            # Get current global stats
            global_stats = self._get_global_statistics()
            
            # Get top countries for trend analysis
            top_countries = self._get_top_countries_data(20)
            
            # Calculate trend indicators
            trends = self._calculate_trend_indicators(top_countries)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(top_countries)
            
            # Generate AI analysis
            analysis = self._generate_trend_analysis(global_stats, trends, anomalies)
            
            result = {
                "global_stats": global_stats,
                "top_countries": top_countries,
                "trends": trends,
                "anomalies": anomalies,
                "ai_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # Convert numpy types
            return self._convert_numpy_types(result)
            
        except Exception as e:
            print(f"❌ Error in global trend analysis: {e}")
            return {"error": str(e)}
    
    def analyze_country_trends(self, country_name: str) -> Dict[str, Any]:
        """Analyze trends for a specific country"""
        try:
            # Get country data
            country_data = self._get_country_data(country_name)
            if not country_data:
                return {"error": f"No data found for {country_name}"}
            
            # Get global context
            global_stats = self._get_global_statistics()
            
            # Calculate country-specific trends
            country_trends = self._calculate_country_trends(country_data, global_stats)
            
            # Generate AI analysis
            analysis = self._generate_country_analysis(country_name, country_data, country_trends, global_stats)
            
            result = {
                "country": country_name,
                "current_stats": country_data,
                "trends": country_trends,
                "global_context": global_stats,
                "ai_analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # Convert numpy types
            return self._convert_numpy_types(result)
            
        except Exception as e:
            print(f"❌ Error in country trend analysis: {e}")
            return {"error": str(e)}
    
    def get_risk_assessment(self) -> Dict[str, Any]:
        """Generate risk assessment for all countries"""
        try:
            # Get all countries data
            all_countries = self._get_all_countries_data()
            
            # Calculate risk scores
            risk_scores = self._calculate_risk_scores(all_countries)
            
            # Generate risk categories
            high_risk = [c for c in risk_scores if c['risk_score'] > 75]
            medium_risk = [c for c in risk_scores if 50 <= c['risk_score'] <= 75]
            low_risk = [c for c in risk_scores if c['risk_score'] < 50]
            
            # Generate AI insights
            risk_analysis = self._generate_risk_analysis(high_risk, medium_risk, low_risk)
            
            result = {
                "high_risk_countries": high_risk,
                "medium_risk_countries": medium_risk,
                "low_risk_countries": low_risk,
                "ai_analysis": risk_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # Convert numpy types
            return self._convert_numpy_types(result)
            
        except Exception as e:
            print(f"❌ Error in risk assessment: {e}")
            return {"error": str(e)}
    
    def _get_global_statistics(self) -> Dict[str, Any]:
        """Get current global statistics"""
        query = """
        MATCH (c:Country)
        RETURN sum(c.confirmed) as total_confirmed,
               sum(c.deaths) as total_deaths,
               sum(c.recovered) as total_recovered,
               count(c) as total_countries,
               avg(c.confirmed) as avg_cases,
               avg(c.deaths) as avg_deaths
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            data = result.single()
            
            return {
                "total_confirmed": int(data["total_confirmed"] or 0),
                "total_deaths": int(data["total_deaths"] or 0),
                "total_recovered": int(data["total_recovered"] or 0),
                "total_countries": int(data["total_countries"] or 0),
                "active_cases": int((data["total_confirmed"] or 0) - (data["total_deaths"] or 0) - (data["total_recovered"] or 0)),
                "global_death_rate": float((data["total_deaths"] or 0) / (data["total_confirmed"] or 1) * 100),
                "global_recovery_rate": float((data["total_recovered"] or 0) / (data["total_confirmed"] or 1) * 100)
            }
    
    def _get_top_countries_data(self, limit: int = 20) -> List[Dict]:
        """Get top countries by confirmed cases"""
        query = """
        MATCH (c:Country)
        RETURN c.name as country, c.confirmed as confirmed, c.deaths as deaths, 
               c.recovered as recovered, c.last_updated as last_updated
        ORDER BY c.confirmed DESC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, {"limit": limit})
            countries = []
            
            for record in result:
                confirmed = int(record["confirmed"] or 0)
                deaths = int(record["deaths"] or 0)
                recovered = int(record["recovered"] or 0)
                
                country_data = {
                    "country": record["country"],
                    "confirmed": confirmed,
                    "deaths": deaths,
                    "recovered": recovered,
                    "active": confirmed - deaths - recovered,
                    "death_rate": float(deaths / confirmed * 100) if confirmed > 0 else 0.0,
                    "recovery_rate": float(recovered / confirmed * 100) if confirmed > 0 else 0.0
                }
                countries.append(country_data)
            
            return countries
    
    def _get_country_data(self, country_name: str) -> Dict[str, Any]:
        """Get data for specific country"""
        query = """
        MATCH (c:Country {name: $country_name})
        RETURN c.name as country, c.confirmed as confirmed, c.deaths as deaths,
               c.recovered as recovered, c.last_updated as last_updated
        """
        
        with self.driver.session() as session:
            result = session.run(query, {"country_name": country_name})
            record = result.single()
            
            if not record:
                return None
            
            confirmed = int(record["confirmed"] or 0)
            deaths = int(record["deaths"] or 0)
            recovered = int(record["recovered"] or 0)
            
            return {
                "country": record["country"],
                "confirmed": confirmed,
                "deaths": deaths,
                "recovered": recovered,
                "active": confirmed - deaths - recovered,
                "death_rate": float(deaths / confirmed * 100) if confirmed > 0 else 0.0,
                "recovery_rate": float(recovered / confirmed * 100) if confirmed > 0 else 0.0
            }
    
    def _get_all_countries_data(self) -> List[Dict]:
        """Get all countries data"""
        query = """
        MATCH (c:Country)
        RETURN c.name as country, c.confirmed as confirmed, c.deaths as deaths, c.recovered as recovered
        ORDER BY c.confirmed DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            countries = []
            
            for record in result:
                confirmed = int(record["confirmed"] or 0)
                if confirmed > 0:  # Only include countries with data
                    deaths = int(record["deaths"] or 0)
                    recovered = int(record["recovered"] or 0)
                    
                    country_data = {
                        "country": record["country"],
                        "confirmed": confirmed,
                        "deaths": deaths,
                        "recovered": recovered,
                        "active": confirmed - deaths - recovered,
                        "death_rate": float(deaths / confirmed * 100),
                        "recovery_rate": float(recovered / confirmed * 100)
                    }
                    countries.append(country_data)
            
            return countries
    
    def _calculate_trend_indicators(self, countries: List[Dict]) -> Dict[str, Any]:
        """Calculate various trend indicators"""
        if not countries:
            return {}
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(countries)
        
        return {
            "avg_death_rate": float(df['death_rate'].mean()),
            "avg_recovery_rate": float(df['recovery_rate'].mean()),
            "high_death_rate_countries": int(len(df[df['death_rate'] > 3.0])),
            "low_recovery_rate_countries": int(len(df[df['recovery_rate'] < 85.0])),
            "countries_with_high_active_cases": int(len(df[df['active'] > 100000])),
            "total_active_cases_top20": int(df['active'].sum()),
            "death_rate_std": float(df['death_rate'].std()),
            "recovery_rate_std": float(df['recovery_rate'].std())
        }
    
    def _detect_anomalies(self, countries: List[Dict]) -> Dict[str, Any]:
        """Detect statistical anomalies in the data"""
        if not countries:
            return {}
        
        df = pd.DataFrame(countries)
        
        # Detect outliers using IQR method
        def detect_outliers(series):
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            return series[(series < lower_bound) | (series > upper_bound)]
        
        death_rate_outliers = detect_outliers(df['death_rate'])
        recovery_rate_outliers = detect_outliers(df['recovery_rate'])
        
        return {
            "countries_with_unusual_death_rates": df.loc[death_rate_outliers.index]['country'].tolist(),
            "countries_with_unusual_recovery_rates": df.loc[recovery_rate_outliers.index]['country'].tolist(),
            "highest_death_rate_country": df.loc[df['death_rate'].idxmax()]['country'],
            "lowest_recovery_rate_country": df.loc[df['recovery_rate'].idxmin()]['country'],
            "death_rate_outlier_values": [float(x) for x in death_rate_outliers.tolist()],
            "recovery_rate_outlier_values": [float(x) for x in recovery_rate_outliers.tolist()]
        }
    
    def _calculate_risk_scores(self, countries: List[Dict]) -> List[Dict]:
        """Calculate risk scores for countries"""
        risk_countries = []
        
        for country in countries:
            # Risk factors (higher = more risk)
            death_rate_score = min(country['death_rate'] * 10, 40)  # Max 40 points
            active_case_score = min(country['active'] / 10000, 30)  # Max 30 points
            low_recovery_score = max(0, (90 - country['recovery_rate']) * 0.5)  # Max 30 points
            
            total_risk_score = death_rate_score + active_case_score + low_recovery_score
            
            risk_countries.append({
                "country": country['country'],
                "confirmed": country['confirmed'],
                "deaths": country['deaths'],
                "active": country['active'],
                "death_rate": country['death_rate'],
                "recovery_rate": country['recovery_rate'],
                "risk_score": float(min(total_risk_score, 100))  # Cap at 100
            })
        
        return sorted(risk_countries, key=lambda x: x['risk_score'], reverse=True)
    
    def _generate_trend_analysis(self, global_stats: Dict, trends: Dict, anomalies: Dict) -> str:
        """Generate AI analysis of global trends using modern LangChain"""
        try:
            # Use modern LangChain syntax: prompt | llm
            data_summary = f"""
            Global COVID-19 Statistics:
            - Total Cases: {global_stats.get('total_confirmed', 0):,}
            - Total Deaths: {global_stats.get('total_deaths', 0):,}
            - Active Cases: {global_stats.get('active_cases', 0):,}
            - Global Death Rate: {global_stats.get('global_death_rate', 0):.2f}%
            - Global Recovery Rate: {global_stats.get('global_recovery_rate', 0):.2f}%
            """
            
            trends_summary = f"""
            Trend Indicators:
            - Average Death Rate (Top 20): {trends.get('avg_death_rate', 0):.2f}%
            - Average Recovery Rate (Top 20): {trends.get('avg_recovery_rate', 0):.2f}%
            - Countries with High Death Rate (>3%): {trends.get('high_death_rate_countries', 0)}
            - Countries with Low Recovery Rate (<85%): {trends.get('low_recovery_rate_countries', 0)}
            - Countries with High Active Cases (>100k): {trends.get('countries_with_high_active_cases', 0)}
            """
            
            anomalies_summary = f"""
            Detected Anomalies:
            - Unusual Death Rates: {', '.join(anomalies.get('countries_with_unusual_death_rates', [])[:5])}
            - Unusual Recovery Rates: {', '.join(anomalies.get('countries_with_unusual_recovery_rates', [])[:5])}
            - Highest Death Rate: {anomalies.get('highest_death_rate_country', 'N/A')}
            - Lowest Recovery Rate: {anomalies.get('lowest_recovery_rate_country', 'N/A')}
            """
            
            # Modern LangChain syntax
            chain = self.trend_analysis_prompt | self.llm
            
            response = chain.invoke({
                "data_summary": data_summary,
                "trends": trends_summary,
                "anomalies": anomalies_summary
            })
            
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            return f"Error generating AI analysis: {str(e)}"
    
    def _generate_country_analysis(self, country: str, current_stats: Dict, trends: Dict, global_context: Dict) -> str:
        """Generate AI analysis for specific country"""
        try:
            current_stats_str = f"""
            - Confirmed Cases: {current_stats['confirmed']:,}
            - Deaths: {current_stats['deaths']:,}
            - Recovered: {current_stats['recovered']:,}
            - Active Cases: {current_stats['active']:,}
            - Death Rate: {current_stats['death_rate']:.2f}%
            - Recovery Rate: {current_stats['recovery_rate']:.2f}%
            """
            
            global_context_str = f"""
            - Global Death Rate: {global_context['global_death_rate']:.2f}%
            - Global Recovery Rate: {global_context['global_recovery_rate']:.2f}%
            - Total Global Cases: {global_context['total_confirmed']:,}
            """
            
            # Modern LangChain syntax
            chain = self.country_analysis_prompt | self.llm
            
            response = chain.invoke({
                "country": country,
                "current_stats": current_stats_str,
                "trend_data": "Real-time data analysis based on current statistics",
                "global_context": global_context_str
            })
            
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            return f"Error generating country analysis: {str(e)}"
    
    def _calculate_country_trends(self, country_data: Dict, global_stats: Dict) -> Dict[str, Any]:
        """Calculate country-specific trend indicators"""
        return {
            "death_rate_vs_global": float(country_data['death_rate'] - global_stats['global_death_rate']),
            "recovery_rate_vs_global": float(country_data['recovery_rate'] - global_stats['global_recovery_rate']),
            "active_case_percentage": float((country_data['active'] / global_stats['active_cases'] * 100) if global_stats['active_cases'] > 0 else 0),
            "case_percentage_of_global": float((country_data['confirmed'] / global_stats['total_confirmed'] * 100) if global_stats['total_confirmed'] > 0 else 0)
        }
    
    def _generate_risk_analysis(self, high_risk: List, medium_risk: List, low_risk: List) -> str:
        """Generate AI analysis of risk assessment"""
        try:
            risk_prompt = PromptTemplate(
                input_variables=["high_risk_summary", "medium_risk_summary", "stats"],
                template="""
                Analyze this COVID-19 risk assessment:

                HIGH RISK COUNTRIES ({high_risk_count}):
                {high_risk_summary}

                MEDIUM RISK COUNTRIES: {medium_risk_count}
                LOW RISK COUNTRIES: {low_risk_count}

                STATISTICS:
                {stats}

                Provide:
                1. **Risk Overview**: Summary of global risk distribution
                2. **High Priority Areas**: Focus on high-risk countries
                3. **Key Risk Factors**: What makes countries high-risk?
                4. **Immediate Actions**: Urgent recommendations
                5. **Monitoring**: Countries to watch closely
                """
            )
            
            high_risk_summary = "\n".join([
                f"- {c['country']}: {c['confirmed']:,} cases, {c['death_rate']:.1f}% death rate, Risk Score: {c['risk_score']:.0f}"
                for c in high_risk[:10]
            ])
            
            stats_summary = f"""
            - Total High Risk Countries: {len(high_risk)}
            - Total Medium Risk Countries: {len(medium_risk)}
            - Total Low Risk Countries: {len(low_risk)}
            - Highest Risk Score: {high_risk[0]['risk_score']:.0f} ({high_risk[0]['country']}) if high_risk else "N/A"
            """
            
            # Modern LangChain syntax
            chain = risk_prompt | self.llm
            
            response = chain.invoke({
                "high_risk_count": len(high_risk),
                "medium_risk_count": len(medium_risk),
                "low_risk_count": len(low_risk),
                "high_risk_summary": high_risk_summary,
                "medium_risk_summary": f"Countries with risk scores 50-75",
                "stats": stats_summary
            })
            
            return response.content if hasattr(response, 'content') else str(response)
            
        except Exception as e:
            return f"Error generating risk analysis: {str(e)}"

# Global instance
trend_analyzer = None

def get_trend_analyzer():
    """Get or create trend analyzer instance"""
    global trend_analyzer
    if trend_analyzer is None:
        trend_analyzer = CovidTrendAnalyzer()
    return trend_analyzer