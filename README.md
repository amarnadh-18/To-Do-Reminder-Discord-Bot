# 📋 To-Do Reminder Discord Bot

A Discord bot for managing tasks and setting reminders with MongoDB integration.

## ✨ Features

- **Task Management**: Create, edit, delete, and complete tasks
- **Smart Reminders**: Set reminders with flexible time formats
- **Priority Levels**: Organize tasks with low, medium, and high priorities
- **MongoDB Storage**: Persistent data storage
- **Rich Embeds**: Beautiful Discord embeds for better UX
- **Time Parsing**: Support for various time formats

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- MongoDB database (local or cloud)
- Discord Bot Token

### Installation

1. **Install dependencies**
   ```bash
   uv sync
   ```

2. **Set up environment variables**
   Copy `.example.env` to `.env` and fill in your values:
   ```bash
   cp .example.env .env
   ```
   Then edit `.env` and set your Discord token and MongoDB URI.

3. **Run the bot**
   ```bash
   python start.py
   ```

## 📖 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!add <title> [description]` | Add a new task | `!add Buy groceries Need milk and bread` |
| `!list [filter]` | List your tasks | `!list completed` |
| `!view <task_id>` | View task details | `!view 507f1f77bcf86cd799439011` |
| `!complete <task_id>` | Mark task as completed | `!complete 507f1f77bcf86cd799439011` |
| `!delete <task_id>` | Delete a task | `!delete 507f1f77bcf86cd799439011` |
| `!edit <task_id> <field> <value>` | Edit a task field | `!edit 507f1f77bcf86cd799439011 title New title` |
| `!remind <task_id> <time> [message]` | Set a reminder | `!remind 507f1f77bcf86cd799439011 in 2 hours Don't forget!` |
| `!priority <task_id> <priority>` | Set task priority | `!priority 507f1f77bcf86cd799439011 high` |
| `!testdm` | Test DM functionality | `!testdm` |
| `!help` | Show help | `!help` |


## 🎯 Priority Levels

- **Low** 🟢 - Green color
- **Medium** 🟡 - Yellow color (default)
- **High** 🔴 - Red color

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DISCORD_TOKEN` | Discord bot token | Yes | - |
| `MONGODB_URI` | MongoDB connection string | No | `mongodb://localhost:27017/` |

### Bot Permissions

The bot requires these permissions:
- Send Messages
- Embed Links
- Read Message History

---

## 🏗️ Project Structure

```
To-Do-Bot/
├── bot.py                 # Main bot file
├── start.py              # Startup script
├── pyproject.toml        # Dependencies
├── README.md            # This file
├── .env                 # Environment variables (not tracked)
├── .env.example         # Example environment file (tracked)
├── db/
│   ├── database.py      # MongoDB connection
│   └── models.py        # Data models
├── cogs/
│   └── tasks.py         # Task commands
├── scheduler/
│   ├── scheduler.py     # APScheduler wrapper
│   └── reminder_jobs.py # Reminder processing
└── utils/
    ├── helpers.py       # Helper functions
    └── timeparser.py    # Time parsing
```

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [discord.py](https://discordpy.readthedocs.io/) - Discord API wrapper
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling
- [PyMongo](https://pymongo.readthedocs.io/) - MongoDB driver
