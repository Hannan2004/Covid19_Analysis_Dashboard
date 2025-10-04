from kafka import KafkaConsumer
import json
import threading
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Neo4j driver
try:
    from .neo4j_client import driver
except ImportError:
    from neo4j_client import driver

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
KAFKA_TOPIC = "covid_data"
KAFKA_GROUP_ID = "covid_group"

# Global variable to track if consumer is running
_consumer_running = False
_consumer_thread = None

def consume_data():
    """Consume messages from Kafka and store in Neo4j"""
    global _consumer_running
    
    if _consumer_running:
        print("⚠️ Consumer already running, skipping...")
        return
    
    _consumer_running = True
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries and _consumer_running:
        try:
            print(f"🔄 Consumer attempt {retry_count + 1}: Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=KAFKA_GROUP_ID,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000,
                consumer_timeout_ms=5000  # 5 second timeout
            )
            
            print("✅ Kafka consumer connected successfully")
            print(f"📡 Listening for messages on topic '{KAFKA_TOPIC}'...")
            
            message_count = 0
            no_message_count = 0
            
            while _consumer_running:
                try:
                    # Poll for messages
                    message_batch = consumer.poll(timeout_ms=1000)
                    
                    if not message_batch:
                        no_message_count += 1
                        if no_message_count % 30 == 0:  # Every 30 seconds
                            print(f"⏳ Waiting for messages... ({no_message_count}s)")
                        continue
                    
                    # Process messages
                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            try:
                                data = message.value
                                message_count += 1
                                print(f"📩 Message #{message_count}: {data}")
                                
                                if not driver:
                                    print("❌ No Neo4j connection available")
                                    continue
                                
                                # Store in Neo4j
                                with driver.session() as session:
                                    query = """
                                    MERGE (c:Country {name: $country})
                                    SET c.confirmed = $confirmed,
                                        c.deaths = $deaths,
                                        c.recovered = $recovered,
                                        c.last_updated = datetime()
                                    """
                                    
                                    # Handle both 'cases' and 'confirmed' field names
                                    confirmed = data.get('confirmed', data.get('cases', 0))
                                    
                                    session.run(query, 
                                        country=data['country'],
                                        confirmed=confirmed,
                                        deaths=data.get('deaths', 0),
                                        recovered=data.get('recovered', 0)
                                    )
                                
                                print(f"✅ Processed data for {data['country']} (Total: {message_count})")
                                
                            except Exception as e:
                                print(f"❌ Error processing message: {e}")
                                continue
                                
                except Exception as e:
                    print(f"❌ Error polling messages: {e}")
                    time.sleep(1)
                    continue
                    
        except Exception as e:
            retry_count += 1
            print(f"❌ Consumer error (attempt {retry_count}): {e}")
            
            if retry_count < max_retries:
                wait_time = min(2 ** retry_count, 30)
                print(f"⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ Failed to connect to Kafka after {max_retries} attempts")
                break
    
    _consumer_running = False
    print("🛑 Consumer stopped")

def start_consumer_thread():
    """Start the consumer in a separate thread"""
    global _consumer_thread, _consumer_running
    
    if _consumer_thread and _consumer_thread.is_alive():
        print("⚠️ Consumer thread already running")
        return _consumer_thread
    
    _consumer_running = False
    _consumer_thread = threading.Thread(target=consume_data, daemon=True)
    _consumer_thread.start()
    print("🚀 Kafka consumer thread started")
    return _consumer_thread

if __name__ == "__main__":
    print("🚀 Starting Kafka Consumer...")
    consume_data()