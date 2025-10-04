from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use localhost for local development
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

def create_producer():
    """Create Kafka producer with proper error handling and retries"""
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🔗 Attempt {retry_count + 1}: Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                request_timeout_ms=30000,
                metadata_max_age_ms=30000,
                max_block_ms=30000,
                retries=5,
                retry_backoff_ms=1000
            )
            print("✅ Kafka producer created successfully")
            return producer
        except Exception as e:
            print(f"❌ Failed to create Kafka producer (attempt {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(5)
    
    print(f"❌ Failed to create producer after {max_retries} attempts")
    return None

def fetch_covid_data():
    """Fetch real COVID data from API with error handling"""
    try:
        print("🌐 Fetching COVID data from API...")
        url = "https://disease.sh/v3/covid-19/countries"
        
        response = requests.get(
            url, 
            timeout=30,
            headers={'User-Agent': 'COVID-Dashboard/1.0'}
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Fetched data for {len(data)} countries")
        return data
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return []

def send_batch_messages(producer, data):
    """Send messages in batch with error handling"""
    successful_sends = 0
    failed_sends = 0
    
    for country_data in data:
        try:
            # Map the API response to our expected format
            message = {
                "country": country_data.get("country", "Unknown"),
                "cases": country_data.get("cases", 0),
                "deaths": country_data.get("deaths", 0),
                "recovered": country_data.get("recovered", 0),
                "timestamp": int(time.time())
            }
            
            # Send message
            future = producer.send("covid_data", value=message)
            result = future.get(timeout=10)
            
            print(f"✅ Sent data for {message['country']}: cases={message['cases']:,}")
            successful_sends += 1
            
        except Exception as e:
            print(f"❌ Failed to send data for {country_data.get('country', 'Unknown')}: {e}")
            failed_sends += 1
    
    print(f"📊 Batch complete: {successful_sends} successful, {failed_sends} failed")
    return successful_sends, failed_sends

def main():
    print("🚀 Starting COVID-19 Data Producer...")
    print("⏳ Waiting for Kafka to be ready...")
    time.sleep(10)  # Reduced wait time for local development
    
    producer = create_producer()
    if not producer:
        print("❌ Cannot create producer, exiting...")
        return
    
    batch_count = 0
    
    try:
        while True:
            batch_count += 1
            print(f"\n🔄 Starting batch #{batch_count} at {datetime.now()}")
            
            # Fetch real data
            data = fetch_covid_data()
            
            if data:
                successful, failed = send_batch_messages(producer, data)
                print(f"✅ Batch #{batch_count} completed successfully")
            else:
                print("⚠️ No data to send")
            
            print(f"😴 Waiting 120 seconds before next batch...")
            time.sleep(120)
            
    except KeyboardInterrupt:
        print("\n🛑 Producer stopped by user")
    except Exception as e:
        print(f"\n❌ Producer error: {e}")
    finally:
        if producer:
            producer.flush()
            producer.close()
            print("🔒 Producer closed")

if __name__ == "__main__":
    from datetime import datetime
    main()