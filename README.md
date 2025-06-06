


<h1 align="center">TelegramUserStats</h1>
<p align="center"><b>TelegramUserStats</b> is a Python script based on <a href="https://github.com/LonamiWebs/Telethon">Telethon</a> that logs into your Telegram account (as a userbot), parses a chat, and sends chat statistics directly to your Telegram.</p>


<p align="center">
    <a href="">
    <img alt="Telethon" src="https://img.shields.io/badge/library-telethon%201.40.0-blue" />
  </a>
  <a href="">
    <img alt="Matplotlib" src="https://img.shields.io/badge/library-matplotlib%203.10.3-blue" />
  </a>
  <a href="">
    <img alt="Python" src="https://img.shields.io/badge/python-3.11-blue" />
  </a>
</p>

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
![448601291-c3692c3e-3a89-4fc2-b8c9-52a00481e480](https://github.com/user-attachments/assets/7e150050-884e-4b57-b4b3-a64a9d04b289)

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
