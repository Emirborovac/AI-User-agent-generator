# User Agent Database Generator

A Python tool that generates and maintains a SQLite database of diverse user agent strings using OpenAI's GPT-4 API. This tool is designed to create a comprehensive collection of user agents with a focus on maintaining a realistic distribution between mobile and desktop devices.

## Features

- Automated generation of realistic user agent strings using OpenAI's GPT-4
- Maintains a balanced distribution (80% mobile, 20% PC) of user agents
- SQLite database storage with duplicate detection
- User agent validation and cleaning
- Device type classification (mobile, tablet, desktop)
- Real-time progress tracking and statistics

## Prerequisites

- Python 3.x
- OpenAI API key
- Required Python packages:
  - openai
  - sqlite3 (usually included with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/user-agent-generator.git
cd user-agent-generator
```

2. Install required packages:
```bash
pip install openai
```

3. Set up your OpenAI API key in the script or as an environment variable.

## Usage

1. Update the OpenAI API key in the script:
```python
openai.api_key = 'your-api-key-here'
```

2. Run the script:
```bash
python user_agent_generator.py
```

The script will:
- Create a SQLite database named 'user_agents.db'
- Generate user agents until reaching 10,000 unique entries
- Display progress and statistics during execution

## Database Structure

The SQLite database contains a single table with the following schema:

```sql
CREATE TABLE user_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_agent TEXT UNIQUE,
    device_type TEXT
)
```

## Key Functions

- `clean_user_agent(user_agent)`: Validates and cleans user agent strings
- `fetch_user_agents()`: Retrieves new user agents from OpenAI API
- `save_to_db(user_agents)`: Stores unique user agents in the database
- `verify_database()`: Checks database integrity and displays samples
- `check_device_distribution()`: Shows device type distribution statistics

## Sample Output

The script provides real-time feedback:
```
Current count: 150. Fetching more user agents...
Successfully inserted: Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X)... (mobile)
Device Type Distribution:
mobile: 120 (80.0%)
desktop: 30 (20.0%)
```

## Error Handling

The script includes comprehensive error handling for:
- API connection issues
- Database operations
- Invalid user agent strings
- Duplicate entries

## Best Practices

1. Monitor your OpenAI API usage to manage costs
2. Regularly backup the SQLite database
3. Check the device type distribution to ensure desired ratios
4. Validate user agents before using them in production

## Security Notes

- Keep your OpenAI API key secure
- Do not commit the API key to version control
- Consider using environment variables for sensitive data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is open source and available under the MIT License.

## Disclaimer

This tool is intended for legitimate testing and development purposes. Please ensure compliance with terms of service when using generated user agents.
