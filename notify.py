import os
import sys
import requests
from groq import Groq
import time

def summarize_logs(error_logs):
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize the following error logs in a concise manner, giving them in bullet points. Only mention the key errors:\n\n{error_logs}",
                }
            ],
            model="llama3-8b-8192",
        )
        summary = chat_completion.choices[0].message.content.strip()
        return summary
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

    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
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
            print(f"Request payload: {data}")
            
            if attempt < 4:  # Don't sleep after the last attempt
                sleep_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    print("Failed to send message after 5 attempts")
def main():
    if len(sys.argv) < 2:
        print("Error: Please provide the path to the error log file as an argument.")
        sys.exit(1)

    error_log_file = sys.argv[1]
    author = sys.argv[2]

    # Read the error logs
    try:
        with open(error_log_file, 'r') as f:
            error_logs = f.read()
    except IOError as e:
        print(f"Error reading error log file: {e}")
        sys.exit(1)

    # Summarize the error logs using Groq API
    summary = summarize_logs(error_logs)

    # Prepare the message
    message = (
    "⚠️ *BUILD FAILED* ⚠️\n\n"
    f"*Author:* {author}\n\n"
    "*Summary:*\n"
    f"{summary}\n\n"
    "Please check the build logs for more details."
)

    # Send the message via Telegram
    send_telegram_message(message)

    
if __name__ == "__main__":
    main()
