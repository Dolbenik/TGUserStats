# TelegramUserStats

**TelegramUserStats** is a Python script based on [Telethon](https://github.com/LonamiWebs/Telethon) that logs into your Telegram account (as a userbot), parses a chat, and sends chat statistics directly to your Telegram.

## 🚀 Features

- Collects and analyzes message data from any chat you're part of
- Sends results directly to your Telegram in a readable format
- Easy command-based interface for requesting different types of statistics

## 📦 Bot Commands (`/starting`)
0. `/instruction` 
1. `/general-info`
2. `/top-users`
3. `/top-media`
4. `/top-days`
5. `/top-words`
6. `/parsing`

## 📘 Instruction (`/instruction`)
1. General statistics of all data
2. Top users by number of messages (text and media)
3. Top media types
4. Top popular days
5. Top popular words
6. Data collection from the chat

## 📸 Example: (Photo)
![img](https://github.com/user-attachments/assets/f2e936e1-542a-424a-a194-778dd403f1ab)

<details><summary>🧩 <strong>Method 0: With <code>console</code></strong></summary>

## 🖥️ Console Installation & Launch
  
0. ⚙️ Installation & Launch
🧬 Clone the repository
    ```bash
    git clone https://github.com/your-username/TelegramUserStats.git
    cd TelegramUserStats
    pip install -r requirements.txt

1. ⚙️ Create configuration file
Inside the data/config file, set your Telegram API credentials:
    ```bash
    API_ID=your_api_id
    API_HASH=your_api_hash

3. ▶️ Run the bot
   ```bash
    python app.py
</details>

<details><summary>🧩 <strong>Method 1: With <code>Docker</code></strong></summary>

## 🐳 Docker Installation & Launch

0. 🧬 **Clone the repository**
   ```bash
   git clone https://github.com/your-username/TelegramUserStats.git
   cd TelegramUserStats

1. ⚙️ Create configuration file
Inside the data/config file, set your Telegram API credentials:
    ```bash
    API_ID=your_api_id
    API_HASH=your_api_hash

2. 🛠️ Build Docker image
    ```bash
    docker build -t telegram-user-stats .

3. ▶️ Run the bot
    ```bash
    docker run --rm -it \
    -v $(pwd)/data:/app/data \
    telegram-user-stats
</details>
