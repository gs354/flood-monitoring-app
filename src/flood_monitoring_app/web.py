import logging
from datetime import datetime

import matplotlib
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse

matplotlib.use("Agg")  # Use non-interactive backend

from .api import get_request_json
from .data import (
    DATA_DIR,
    N_LIMIT,
    PLOTS_DIR,
    ROOT_URL,
    extract_readings,
    load_station_ids,
    save_readings_to_csv,
    validate_station_id,
)
from .plotting import plot_data

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Flood Monitoring App")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
async def home():
    """Render form for entering station ID and parameters."""
    return """
    <html>
        <body>
            <h1>Flood Monitoring Data</h1>
            <form action="/monitor" method="get">
                <p>Station ID: <input type="text" name="station_id" required></p>
                <p>Days back: <input type="number" name="days_back" value="1" min="1" max="14"></p>
                <input type="submit" value="Get Data">
            </form>
        </body>
    </html>
    """


@app.get("/monitor")
async def monitor_station(station_id: str, days_back: int = 1):
    """Get and display monitoring data for a station."""
    try:
        logger.info(
            f"Processing request for station {station_id}, days_back={days_back}"
        )

        # Validate inputs
        try:
            valid_ids = load_station_ids()
            validate_station_id(station_id, valid_ids)
        except FileNotFoundError:
            logger.warning("Station IDs file not found, skipping validation")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Get data
        try:
            readings = get_request_json(
                f"{ROOT_URL}/{station_id}/readings?_limit={N_LIMIT}"
            )
            measures_data = extract_readings(readings)
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error fetching data from API: {str(e)}"
            )

        # Create timestamp
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M")

        # Ensure directories exist
        PLOTS_DIR.mkdir(parents=True, exist_ok=True)
        csv_dir = DATA_DIR / "readings"
        csv_dir.mkdir(parents=True, exist_ok=True)

        # Save CSVs
        try:
            save_readings_to_csv(
                readings=measures_data,
                output_dir=csv_dir,
                station_id=station_id,
                timestamp=timestamp,
            )
            logger.info("CSV files saved successfully")
        except Exception as e:
            logger.error(f"Error saving CSV files: {e}")
            raise HTTPException(status_code=500, detail="Error saving data files")

        # Create plot
        try:
            plot_path = PLOTS_DIR / f"station_{station_id}_{timestamp}.png"
            logger.info(f"Attempting to create plot at {plot_path}")
            logger.info(f"Measures data: {list(measures_data.keys())}")

            plot_data(
                data=measures_data,
                savefig=True,
                filepath=plot_path,
                format="png",
            )
            logger.info(f"Plot saved to {plot_path}")
        except Exception as e:
            logger.error(
                f"Error creating plot: {e}", exc_info=True
            )  # Add full traceback
            raise HTTPException(
                status_code=500, detail=f"Error creating plot: {str(e)}"
            )

        # Get list of CSV files
        csv_files = list(csv_dir.glob(f"station_{station_id}_*_{timestamp}.csv"))

        # Return results page
        return HTMLResponse(f"""
        <html>
            <body>
                <h1>Results for Station {station_id}</h1>
                <h2>Plot</h2>
                <img src="/plot/{plot_path.name}" alt="Station readings plot" />
                <h2>Data Files</h2>
                <ul>
                    {
            " ".join(
                f'<li><a href="/data/{f.name}">{f.name}</a></li>' for f in csv_files
            )
        }
                </ul>
                <p><a href="/">Back to form</a></p>
            </body>
        </html>
        """)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/plot/{filename}")
async def get_plot(filename: str):
    """Serve plot file."""
    try:
        return FileResponse(PLOTS_DIR / filename)
    except Exception as e:
        logger.error(f"Error serving plot {filename}: {e}")
        raise HTTPException(status_code=404, detail="Plot not found")


@app.get("/data/{filename}")
async def get_data(filename: str):
    """Serve CSV file."""
    try:
        return FileResponse(DATA_DIR / "readings" / filename)
    except Exception as e:
        logger.error(f"Error serving data file {filename}: {e}")
        raise HTTPException(status_code=404, detail="Data file not found")
