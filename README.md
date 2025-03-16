# Elon Line Bot

A LINE chatbot that simulates conversations with Elon Musk, complete with Tesla facts, SpaceX updates, and Elon's signature wit.

## Features

- Elon Musk-style responses
- Tesla and SpaceX facts
- Weather updates
- News updates
- Task execution
- Famous Elon Musk quotes
- Personal advice from "Elon"

## Commands

- `/help` - Show available commands
- `/tesla` - Get Tesla facts
- `/spacex` - Get SpaceX facts
- `/quote` - Get Elon Musk quotes
- `/weather [location]` - Get weather info
- `/news` - Get latest news
- `/advice` - Get advice from Elon
- `/task [task_name]` - Execute a task
- `/random` - Get random Elon-style response

## Setup

### Prerequisites

- Python 3.8+
- AWS Account
- LINE Messaging API account
- OpenAI API key (optional)

### Environment Variables

Set up the following environment variables:

```bash
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
```

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/elon-line-bot.git
cd elon-line-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

## Deployment

1. Create a Lambda function in AWS
2. Set up environment variables in Lambda
3. Deploy the code to Lambda
4. Configure LINE webhook URL to point to your Lambda function

## Development

```bash
# Run tests
python -m pytest

# Local development
python lambda_function.py
```
