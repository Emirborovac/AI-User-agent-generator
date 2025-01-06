import openai
import sqlite3
import time
import json
import re

# OpenAI API Key
openai.api_key = 'YOUR API'

# SQLite database setup
db_name = 'user_agents.db'
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Drop and recreate the table
cursor.execute('DROP TABLE IF EXISTS user_agents')
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_agent TEXT UNIQUE,
    device_type TEXT
)
''')
conn.commit()

def clean_user_agent(user_agent):
    """Clean and validate a user agent string."""
    # Remove any leading numbers or trailing numbers
    cleaned = re.sub(r'^\d+|^\s+|\s+$', '', user_agent)
    
    # Check if it's a valid user agent
    if (
        cleaned.startswith('Mozilla') and 
        len(cleaned) > 20 and 
        ('Chrome' in cleaned or 'Firefox' in cleaned or 'Safari' in cleaned)
    ):
        return cleaned
    return None

def split_concatenated_user_agents(text):
    """Split concatenated user agents into individual ones."""
    # Split by numbers followed by Mozilla
    agents = re.split(r'\d+(?=Mozilla)', text)
    # Clean each agent
    valid_agents = []
    for agent in agents:
        cleaned = clean_user_agent(agent)
        if cleaned:
            valid_agents.append(cleaned)
    return valid_agents

def fetch_user_agents():
    """Fetch 10 user agents (80% mobile, 20% PC) from OpenAI API."""
    prompt = (
        "Generate 10 unique up-to-date user agents in JSON format. "
        "Ensure 80% are mobile user agents and 20% are PC user agents. "
        "Each user agent should be in this format: "
        "{'user_agent': '...', 'device_type': '...'} where device_type is exactly one of: "
        "'mobile', 'tablet', or 'desktop'. Make sure each user agent string is complete "
        "and properly formatted. Make them authentic and suitable for use in applications."
    )
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4", #or gpt-4o
            messages=[
                {"role": "system", "content": "You are an assistant that generates Turkish user agents."},
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.choices[0].message.content.strip()
        
        start_marker = "```json\n"
        end_marker = "\n```"
        
        if start_marker in content and end_marker in content:
            json_str = content[content.find(start_marker) + len(start_marker):content.rfind(end_marker)]
            user_agents = json.loads(json_str)
            return user_agents
        else:
            import re
            json_match = re.search(r'\[\s*{.*}\s*\]', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                print("Could not find valid JSON in response")
                return []
            
    except Exception as e:
        print(f"Error fetching user agents: {e}")
        return []

def save_to_db(user_agents):
    """Save unique user agents to the database."""
    successful_inserts = 0
    
    # Handle both list of dictionaries and list of strings
    if isinstance(user_agents, list):
        if all(isinstance(x, dict) for x in user_agents):
            agents_to_save = [(agent['user_agent'], agent.get('device_type', 'unknown')) for agent in user_agents]
        else:
            agents_to_save = [(agent, 'unknown') for agent in user_agents]
    else:
        agents_to_save = [(agent, 'unknown') for agent in split_concatenated_user_agents(user_agents)]
    
    for agent, device_type in agents_to_save:
        try:
            cleaned_agent = clean_user_agent(agent)
            if cleaned_agent:
                cursor.execute('INSERT INTO user_agents (user_agent, device_type) VALUES (?, ?)', 
                             (cleaned_agent, device_type))
                conn.commit()
                successful_inserts += 1
                print(f"Successfully inserted: {cleaned_agent[:100]}... ({device_type})")
        except sqlite3.IntegrityError:
            print(f"Duplicate user agent skipped")
        except Exception as e:
            print(f"Error saving user agent: {e}")
    
    return successful_inserts

def get_user_agent_count():
    """Get the total count of unique user agents in the database."""
    cursor.execute('SELECT COUNT(*) FROM user_agents')
    return cursor.fetchone()[0]

def verify_database():
    """Verify database entries."""
    cursor.execute('SELECT user_agent, device_type FROM user_agents')
    agents = cursor.fetchall()
    print(f"\nTotal unique user agents in database: {len(agents)}")
    print("\nSample of stored user agents:")
    for agent, device_type in agents[:5]:
        print(f"- [{device_type}] {agent}")

def check_device_distribution():
    """Check the distribution of device types in the database."""
    cursor.execute('''
        SELECT device_type, COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM user_agents), 2) as percentage
        FROM user_agents
        GROUP BY device_type
    ''')
    distribution = cursor.fetchall()
    print("\nDevice Type Distribution:")
    for device_type, count, percentage in distribution:
        print(f"{device_type}: {count} ({percentage}%)")

def main():
    """Main loop to fetch and save user agents until 10,000 unique entries."""
    try:
        # First, let's handle any existing concatenated user agents
        cursor.execute('SELECT user_agent FROM user_agents')
        existing_agents = cursor.fetchall()
        
        if existing_agents:
            print("Processing existing user agents...")
            cursor.execute('DROP TABLE IF EXISTS user_agents')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_agent TEXT UNIQUE,
                    device_type TEXT
                )
            ''')
            conn.commit()
            
            for agent in existing_agents:
                split_agents = split_concatenated_user_agents(agent[0])
                for split_agent in split_agents:
                    save_to_db([split_agent])
        
        while True:
            user_agent_count = get_user_agent_count()
            if user_agent_count >= 10000:
                print("\nDatabase now contains 10,000 unique user agents. Task complete!")
                verify_database()
                check_device_distribution()
                break
            
            print(f"\nCurrent count: {user_agent_count}. Fetching more user agents...")
            user_agents = fetch_user_agents()
            
            if user_agents:
                successful = save_to_db(user_agents)
                print(f"Successfully added {successful} new user agents")
                check_device_distribution()  # Show distribution after each batch
            else:
                print("Failed to fetch user agents. Retrying in 10 seconds...")
                time.sleep(10)
    
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        verify_database()
        check_device_distribution()
        conn.close()

if __name__ == '__main__':
    main()