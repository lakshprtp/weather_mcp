import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import JSONResponse

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Initialize FastMCP server
mcp = FastMCP(
    "Weather Server",
    host=HOST,
    port=PORT,
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    """Health check and server info endpoint for web browsers and monitoring."""
    return JSONResponse(
        {
            "status": "online",
            "service": "Weather MCP Server",
            "sse_endpoint": "/sse",
            "messages_endpoint": "/messages/",
        }
    )


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy"})


@mcp.tool()
def get_current_weather(city: str):
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        },
    )

    data = response.json()

    if response.status_code != 200:
        return data

    return {
        "city": data.get("name", city),
        "temperature_c": data.get("main", {}).get("temp"),
        "feels_like_c": data.get("main", {}).get("feels_like"),
        "humidity": data.get("main", {}).get("humidity"),
        "condition": (data.get("weather") or [{}])[0].get("description"),
        "wind_speed": data.get("wind", {}).get("speed"),
    }


@mcp.tool()
def get_forecast(city: str):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric",
    }

    response = requests.get(url, params=params)

    data = response.json()

    if response.status_code != 200:
        return data

    forecast = []

    # Return first 5 forecast entries
    for item in data.get("list", [])[:5]:
        forecast.append(
            {
                "datetime": item.get("dt_txt"),
                "temperature": item.get("main", {}).get("temp"),
                "weather": (item.get("weather") or [{}])[0].get("description"),
            }
        )

    return {
        "city": city,
        "forecast": forecast,
    }


# Expose ASGI application
app = mcp.sse_app()

if __name__ == "__main__":
    # When deployed to Render or when PORT is set, default to SSE transport
    transport_mode = os.getenv("MCP_TRANSPORT", "sse" if "PORT" in os.environ else "stdio")
    if transport_mode == "sse":
        mcp.run(transport="sse")
    elif transport_mode == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
