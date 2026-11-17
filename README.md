# Weather MCP Server

A Model Context Protocol (MCP) server that provides real-time weather and forecast data using the OpenWeatherMap API, built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk).

## Features

- **`get_current_weather(city)`**: Returns temperature, feels-like, humidity, condition, and wind speed.
- **`get_forecast(city)`**: Returns a 5-step forecast for the requested city.
- **Streamable HTTP Transport**: Operates over Streamable HTTP (`/mcp`) for cloud hosting on platforms like Render.
- **Built-in Health Checks**: Endpoints at `/` and `/health` for uptime monitoring and browser verification.

---

## Local Setup

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd weather_mcp
   ```

2. **Create a virtual environment and install dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Add your OpenWeatherMap API key:
   ```env
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

4. **Run the server locally**:
   - **Local stdio mode** (for local CLI/desktop MCP clients):
     ```bash
     python mcp_server.py
     ```
   - **Local HTTP mode** (web server):
     ```bash
     MCP_TRANSPORT=streamable-http PORT=8000 python mcp_server.py
     ```
     Visit `http://localhost:8000` or `http://localhost:8000/health` in your browser.

---

## Deploy to Render

### Option 1: Blueprints (Automatic)
1. Push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), click **New +** > **Blueprint**.
3. Connect your GitHub repository. Render reads [`render.yaml`](render.yaml) automatically.
4. When prompted, enter your `OPENWEATHER_API_KEY`.
5. Click **Apply**.

### Option 2: Manual Web Service
1. In the [Render Dashboard](https://dashboard.render.com/), click **New +** > **Web Service**.
2. Connect your GitHub repository.
3. Configure the settings:
   - **Name**: `weather-mcp-server`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python mcp_server.py`
   - **Plan**: `Free`
4. Add the following **Environment Variables**:
   - `OPENWEATHER_API_KEY`: *(Your OpenWeather API key)*
   - `PYTHON_VERSION`: `3.11.10`
   - `MCP_TRANSPORT`: `streamable-http`
   - `HOST`: `0.0.0.0`
5. Click **Deploy Web Service**.

Once deployed, your MCP server will be live at:
- **HTTP Endpoint**: `https://<your-subdomain>.onrender.com/mcp`
- **Health Check**: `https://<your-subdomain>.onrender.com/health`

---

## Connecting to MCP Clients (Cursor, Claude Desktop, etc.)

Add the following to your MCP client configuration:

```json
{
  "mcpServers": {
    "weather": {
      "url": "https://<your-subdomain>.onrender.com/mcp"
    }
  }
}
```
