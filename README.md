# SPErg

SPErg is a basic Flask based web application developed as part of a Systems Programming course for the Summer Semester 2025.

## Overview

The application is designed to serve betting recommendations to clients. It features:

- A Flask backend to handle routing and responses.
- A state of the art database ("mydatabase.db")
- Integration with Redis to allow clients to upload specific data directly to the database.
- Modular structure for ease of testing among other things.

## Technologies Used

- **Python**
- **Flask**
- **Redis**
- **Docker** (optional for the app, required for redis/rq)

## Getting Started

### Requirements

Ensure you have the following installed:

- Flask
- Flask-SQLAlchemy
- RestrictedPython
- sqlalchemy
- redis
- rq

### Installation

1. Clone the repo

   ```bash
   git clone https://github.com/fischdoc/sperg.git
   cd sperg

2. Set up Docker

   ```bash
   docker-compose --build
   docker-compose up web redis

3. Run workers separately (5 workers)

   ```bash
   docker-compose up --scale rqworker=5


## Testing / Use cases

After all the above is done, you can run the following tests.

1. Simulate Clients

   ```bash
   python ./simulate_clients.py

2. Endpoints

   > __GET__ /recommendation/\<int:user_id\>/\<int:score_home\>/\<int:score_away\>
   - Gets recommendations for a certain user. Generates a coupon, but it doesn't count as bought yet. Coupon sales are handled by clients.
   
   > __POST__ /config/\<int:opap_id\>
   - Send a config schema, flags, custom code, etc.

   > __GET__ /config/\<int:opap_id\>
   - Get config json


## License

This project is not licensed. You may steal at will.