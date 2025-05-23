# 📘 CBSE Result Tracker

A lightweight Python-based monitor that checks the [CBSE Results website](https://results.cbse.nic.in/) for Class XII 2025 results and notifies via Discord when updates are detected. Built with GitHub Actions for automated checks every 10 minutes.

---

## 📌 Features

- ⏱️ Auto-checks the CBSE site every 10 minutes using GitHub Actions  
- 🔍 Detects updates for **CBSE 2025 results** 
- 💬 Sends alerts to a Discord channel with detailed info  
- 🧠 Intelligent hashing ensures accurate change detection  
- 📤 Auto-commits updated hash files to GitHub  

---

## 🛠️ Setup Guide

### 1. **Fork the Repository**
Click on the top right of this page → **Fork**

### 2. **Add GitHub Secrets**
Go to your fork → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Name                 | Description                            |
|----------------------|----------------------------------------|
| `DISCORD_TOKEN`      | Your Discord bot token                 |
| `DISCORD_CHANNEL_ID` | Channel ID where alerts are sent       |
| `DEBUG_ID`           | Channel ID for debug messages          |

### 3. **Enable Write Permissions**
- Go to **Settings > Actions > General**
- Under **Workflow permissions**, select **Read and write permissions**
- Click **Save**

---

## 🤖 Bot Behavior

- On every run:
  - Fetches the latest [site]((https://results.cbse.nic.in/)) data
  - Checks for lines with keywords `2025`, `xii`, and `result(s)`
  - Computes and compares an MD5 hash of relevant lines
  - Posts alerts only if there's a meaningful change on the `DISCORD_CHANNEL_ID`

---

## 🔄 Sample Output

```bash
Old Hash: d41d8cd98f00b204e9800998ecf8427e
New Hash: a78b57d9cfca0ffb12ea33a438cc9a9c
Change detected: 2025 update.```
