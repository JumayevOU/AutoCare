# AutoCare Bot

🚗 **AutoCare System** – A Telegram bot that helps users find nearby auto services and car washes in Uzbekistan using location-based search.

## Features

- 📍 **Location-Based Search**: Find nearest autoservices and carwashes based on your location
- 🗺️ **Map Integration**: View locations on Google Maps
- ⚙️ **Service Filters**: Filter by specific services (electrical, body work, tire services, etc.)
- 🕒 **Working Hours**: See operating hours and 24/7 availability
- 📞 **Direct Contact**: Call services directly from Telegram
- 🇺🇿 **Uzbek Language**: Interface in Uzbek language

## Technologies

- **Python 3.12+**
- **aiogram 3.22.0** - Modern Telegram Bot framework
- **PostgreSQL** - Database for storing service locations
- **asyncpg** - Async PostgreSQL driver
- **python-dotenv** - Environment variable management

## Prerequisites

- Python 3.12 or higher
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/PharmaUz/AutoCare.git
cd AutoCare
```

### 2. Install dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using pipenv:
```bash
pipenv install
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here

# Admin Settings
ADMINS=123456789,987654321
ADMIN_GROUP_ID=-1002765600267

# Network Settings
IP=localhost

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
```

### 4. Initialize the database

Run the migration script to create tables and populate initial data:

```bash
python migrate.py
```

### 5. Run the bot

```bash
python app.py
```

## Project Structure

```
AutoCare/
├── app.py                      # Main application entry point
├── database.py                 # Database operations and queries
├── loader.py                   # Bot and dispatcher initialization
├── migrate.py                  # Database migration script
├── requirements.txt            # Python dependencies
├── Pipfile                     # Pipenv configuration
├── .env.example               # Environment variables template
├── data/                       # Configuration and data
│   ├── config.py              # App configuration
│   └── locations.py           # Location data
├── handlers/                   # Message and callback handlers
│   ├── __init__.py
│   ├── users/                 # User-facing handlers
│   │   ├── start.py          # /start command
│   │   ├── menuHendlers.py   # Menu navigation
│   │   └── locations_hendler.py  # Location processing
│   └── errors/                # Error handlers
│       └── error_handler.py
├── keyboards/                  # Keyboard layouts
│   ├── inline/                # Inline keyboards
│   └── default/               # Reply keyboards
├── middlewares/                # Bot middlewares
│   └── rate_limit.py          # Rate limiting
├── utils/                      # Utility functions
│   └── misc/
│       ├── get_distance.py    # Distance calculations
│       └── logging.py         # Logging configuration
├── states/                     # FSM states
└── security/                   # Security documentation
    └── security-checklist.md  # Security review checklist
```

## Database Schema

### autoservice table
- `id` - Unique identifier
- `name` - Service name
- `lat`, `lon` - GPS coordinates
- `address` - Full address
- `phone` - Contact phone
- `services` - Available services (JSONB)
- `working_days` - Working days (array)
- `working_hours` - Operating hours (JSONB)
- `is_24_7` - 24/7 availability flag

### carwash table
Same structure as autoservice

## Usage

1. Start the bot: Send `/start` to your bot
2. Choose service type: Select "Avtoservis" or "Avtomoyka"
3. Select service category (for autoservices)
4. Share your location
5. View nearby results with details
6. Tap on location to view on map or contact the service

## Features in Detail

### Rate Limiting
- Prevents spam by limiting requests to 1 per second for messages
- Callback queries limited to 0.5 seconds
- Automatic rate limit notifications

### Input Validation
- Validates GPS coordinates
- Sanitizes user inputs
- Validates callback data

### Database Optimization
- Connection pooling (1-10 connections)
- Parameterized queries for security
- Haversine formula for accurate distance calculation
- Indexed columns for fast queries

### Error Handling
- Comprehensive error catching
- User-friendly error messages
- Detailed logging for debugging

## Security

This project follows security best practices:
- ✅ Parameterized database queries (SQL injection prevention)
- ✅ Environment variables for sensitive data
- ✅ Input validation and sanitization
- ✅ Rate limiting to prevent abuse
- ✅ Coordinate validation
- ✅ Secure error handling

See [security/security-checklist.md](security/security-checklist.md) for complete security guidelines.

## Development

### Adding New Services

1. Update `data/locations.py` with new service data
2. Run migration: `python migrate.py`

### Testing

Currently, there is no automated test suite. Manual testing recommended:

```bash
# Test database connection
python database.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Open an issue on GitHub
- Contact the maintainers

## Roadmap

- [ ] Add admin panel
- [ ] Implement user reviews and ratings
- [ ] Add fuel delivery service
- [ ] Add anti-theft system integration
- [ ] Multi-language support (Russian, English)
- [ ] Service booking system
- [ ] Push notifications
- [ ] Statistics and analytics

## Authors

- **PharmaUz Team** - Initial work

## Acknowledgments

- aiogram community for the excellent framework
- Contributors and testers
