import os
import sys
import requests
from groq import Groq
import time
import re

def format_message(author, summary, github_actions_url):
    message = f"""⚠️ *BUILD FAILED* ⚠️

*Author:* {author}

*Summary:*
Here are the key errors summarized:

{summary}

[View GitHub Actions Log]({github_actions_url})

Please check the build logs for more details."""
    return message

def escape_markdown_v2(text):
    """Escape special characters for Telegram MarkdownV2 format."""
    escape_chars = '_[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

def clean_and_format_summary(summary):
    # Remove any introductory text
    summary = re.sub(r'^.*?•', '•', summary, flags=re.DOTALL)
    
    # Replace bullet points with asterisks
    summary = summary.replace('•', '*')
    
    # Ensure each bullet point is on a new line
    summary = re.sub(r'(\*[^\n]*?)(\*)', r'\1\n\2', summary)
    
    # Bold the main points
    summary = re.sub(r'\*(.*?):', r'*\1*:', summary)
    
    return summary.strip()


def summarize_logs(error_logs):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following error logs in a concise manner, giving them in bullet points. Do not include any introductory text or formatting instructions. Focus on linting, as well as unittest errors. Include other errors if available. Start directly with the bullet points:\n\n{error_logs}",
                }
            ],
            model="llama3-8b-8192",
        )
        summary = chat_completion.choices[0].message.content.strip()
        return clean_and_format_summary(summary)
    except Exception as e:
        print(f"Error in summarizing logs: {e}")
        return "Failed to summarize logs due to an error."

def send_telegram_message(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    # Escape the message for MarkdownV2, but preserve existing bold formatting and links
    def escape_except_bold_and_links(match):
        if match.group(1):  # Bold text
            return f'*{escape_markdown_v2(match.group(1))}*'
        elif match.group(2) and match.group(3):  # Link
            return f'[{escape_markdown_v2(match.group(2))}]({match.group(3)})'
        else:
            return escape_markdown_v2(match.group(0))

    pattern = r'\*(.*?)\*|\[(.*?)\]\((.*?)\)|.'
    escaped_message = re.sub(pattern, escape_except_bold_and_links, message, flags=re.DOTALL)

    data = {
        "chat_id": chat_id,
        "text": escaped_message,
        "parse_mode": "MarkdownV2"
    }

    for attempt in range(5):
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            print(f"Message sent successfully on attempt {attempt + 1}")
            print(f"Response: {response.text}")
            return  # Exit the function if successful
        except requests.exceptions.RequestException as e:
            print(f"Error sending message (Attempt {attempt + 1}/5): {e}")
            print(f"Response content: {e.response.content if e.response else 'No response'}")
            if attempt < 4:
                sleep_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    print("Failed to send message after 5 attempts")

def format_summary(summary):
    formatted_summary = ""
    for line in summary.split('\n'):
        if line.strip():
            if not line.startswith('*'):
                formatted_summary += f"* {line}\n"
            else:
                formatted_summary += f"{line}\n"
    return formatted_summary.strip()

def main():
    if len(sys.argv) < 3:
        print("Error: Please provide the path to the error log file as an argument.")
        sys.exit(1)

    error_log_file = sys.argv[1]
    author = sys.argv[2]
    github_actions_url = sys.argv[3]

    # Read the error logs
    try:
        with open(error_log_file, 'r') as f:
            error_logs = f.read()
    except IOError as e:
        print(f"Error reading error log file: {e}")
        sys.exit(1)

    # Summarize the error logs using Groq API
    summary = format_summary(summarize_logs(error_logs))

    # Format the message
    message = format_message(author, summary, github_actions_url)

    # Send the message via Telegram
    send_telegram_message(message)

if __name__ == "__main__":
    main()