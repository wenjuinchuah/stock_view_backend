# Stock View Backend

This is the backend application for the Stock View system.

## Prerequisites

- Python (version 3.8+ recommended)
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/wenjuinchuah/stock_view_backend.git
   cd stock_view_backend

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt

## Running the Application

1. Start the development server:
   ```bash
   uvicorn app.main:app --reload

2. Open your browser and navigate to `http://localhost:8000`.

## Docker

### Building and Running with Docker Compose

1. Build the Docker compose image:
   ```bash
   docker-compose up --build

### Troubleshooting

- Ensure that Docker Desktop is correctly installed and running.
- Verify that you have unzipped the code correctly and the folder structure is as specified.
  ```bash
  stock_view/
  ├── stock_view_frontend/
  └── stock_view_backend/
- Verify that you are navigate to the project folder (stock_view_backend).
  ```bash
  cd path/to/stock_view/stock_view_backend/
- Check for any error messages in the terminal and refer to the documentation or online resources for troubleshooting tips.
