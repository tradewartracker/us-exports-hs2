# US Exports HS2 Product Data Visualization

An interactive Bokeh web application for visualizing US export data by country and 2-digit Harmonized System (HS2) product categories. The application features country flags, color-coded lines, and downloadable charts and data.

## Live Demo

The application is deployed on Heroku: [us-exports-hs2.herokuapp.com](https://us-exports-hs2.herokuapp.com)

## Project Overview

This repository contains tools for:
- Downloading US export data from the Census Bureau API
- Processing and enriching the data with country flags and colors
- Displaying interactive visualizations with Bokeh
- Deploying the application to Heroku

## Technology Stack

### Core Technologies
- **Python 3.10**: Main programming language
- **Bokeh 2.0.0**: Interactive visualization framework
- **Pandas**: Data manipulation and analysis
- **PyArrow**: Efficient data storage with Parquet format
- **NumPy**: Numerical computing

### Deployment
- **Heroku**: Cloud platform for hosting the application
- **Git**: Version control

### Data Source
- **US Census Bureau International Trade API**: Export data by country and HS code

## Repository Structure

```
us-exports-hs2/
├── main-exports-hs2.py          # Main Bokeh server application
├── make-exports-hs2-dataset.ipynb    # Data download notebook
├── make-flags-color.ipynb       # Data enrichment notebook
├── requirements.txt             # Python dependencies
├── runtime.txt                  # Python version for Heroku
├── Procfile                     # Heroku deployment configuration
├── data/
│   ├── top30-HS2-exports.parquet    # Main processed dataset
└── README.md                    # This file
```

## Setup and Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd us-exports-hs2
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Bokeh server**
   ```bash
   bokeh serve main-exports-hs2.py --show
   ```
   
   The application will open in your browser at `http://localhost:5006/main-exports-hs2`

## Data Pipeline

### 1. Download Raw Data

Use the `make-exports-hs2-dataset.ipynb` notebook to download export data from the Census Bureau API:

**Steps:**
1. Open the notebook in Jupyter
2. Set your Census API key (get one free at [census.gov/developers](https://www.census.gov/developers/))
3. Update the `date` variable to the current month (format: "YYYY-MM")
4. Run all cells to download data for top 30+ countries

**What it does:**
- Queries the Census Bureau API for HS2-level export data
- Downloads data for the top 30 trading partners by export volume
- Saves individual monthly parquet files to `data/exports/`
- Combines data into consolidated dataset

### 2. Process and Enrich Data

Use the `make-flags-color.ipynb` notebook to add visual metadata:

**Steps:**
1. Open the notebook
2. Run all cells in order

**What it does:**
- Loads the consolidated parquet file (`top30-HS2-exports.parquet`)
- Maps country names to flag URLs (from flagcdn.com)
- Maps country names to representative colors (based on flag colors)
- Saves the enriched data back to the parquet file

**Country mappings include:**
- 30+ major trading partners
- Special aggregates (ALL COUNTRIES, EUROPEAN UNION, USMCA/NAFTA)
- Flag icons and color codes for each country

### 3. Run the Visualization

The `main-exports-hs2.py` file creates an interactive Bokeh application:

**Features:**
- **Multi-country selection**: Compare multiple countries simultaneously
- **Product filtering**: Select from 97 HS2 product categories or view all products
- **Metric options**: View in US Dollars or Year-over-Year % Change
- **Interactive tooltips**: Hover to see country flags, values, and dates
- **Color-coded lines**: Each country displays in its flag color
- **Clickable legend**: Hide/show individual country lines
- **Data export**: Download current selection as CSV
- **Chart export**: Save chart as PNG using toolbar icon

**Application structure:**
- Data loading and indexing by country, product, and time
- Interactive plot generation with Bokeh
- Download functionality for data and charts
- Responsive layout with controls sidebar

## Heroku Deployment

### Prerequisites
- Heroku account ([signup.heroku.com](https://signup.heroku.com/))
- Heroku CLI installed ([devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli))
- Git installed

### Deployment Steps

1. **Login to Heroku**
   ```bash
   heroku login
   ```

2. **Create a new Heroku app** (if not already created)
   ```bash
   heroku create us-exports-hs2
   ```

3. **Configure buildpacks**
   ```bash
   heroku buildpacks:set heroku/python
   ```

4. **Deploy the application**
   ```bash
   git add .
   git commit -m "Update application"
   git push heroku main
   ```

5. **Scale the web dyno**
   ```bash
   heroku ps:scale web=1
   ```

6. **Open the application**
   ```bash
   heroku open
   ```

### Key Heroku Files

**`Procfile`**: Defines the command to run the application
```
web: bokeh serve --port=$PORT --allow-websocket-origin=us-exports-hs2.herokuapp.com --address=0.0.0.0 --use-xheaders main-exports-hs2.py
```

**`runtime.txt`**: Specifies Python version
```
python-3.10
```

**`requirements.txt`**: Lists all Python dependencies

### Heroku Configuration

- **Dyno type**: Standard or Eco (basic web dyno)
- **Port**: Automatically assigned via `$PORT` environment variable
- **WebSocket origin**: Configured to accept connections from the Heroku domain
- **Address binding**: `0.0.0.0` to accept external connections

### Updating Data on Heroku

To update the deployed application with new data:

1. Run the data download notebook locally to get latest data
2. Run the flags-color notebook to enrich the data
3. Commit the updated parquet file(s):
   ```bash
   git add data/top30-HS2-exports.parquet
   git commit -m "Update data for [Month Year]"
   git push heroku main
   ```

## Data Details

### HS2 Product Categories

The application uses 2-digit Harmonized System (HS) codes, which include:
- 97 distinct product categories (HS codes 01-97)
- Examples: Agricultural products, machinery, chemicals, textiles, etc.
- "ALL PRODUCTS" aggregate for total trade

### Countries Covered

Top 30+ US trading partners including:
- Major partners: China, Mexico, Canada, Japan, Germany, UK
- Regional aggregates: European Union, USMCA (NAFTA)
- Emerging markets: Vietnam, India, Brazil, etc.

### Time Range

- Historical data from 2013 onwards
- Monthly frequency
- Updated regularly via Census Bureau API

### Data Structure

The main dataset (`top30-HS2-exports.parquet`) has:
- **MultiIndex**: CTY_NAME, E_COMMODITY_SDESC, time
- **Columns**: E_COMMODITY, exports, flag, color
- **Format**: Parquet (efficient compressed columnar storage)

## Troubleshooting

### Local Development Issues

**Bokeh server won't start:**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)
- Try specifying the port: `bokeh serve main-exports-hs2.py --port=5007`

**No data showing:**
- Verify the parquet file exists: `data/top30-HS2-exports.parquet`
- Check that flag and color columns are present (run make-flags-color.ipynb)
- Look for error messages in the terminal

**CSV download not working:**
- Check browser console for JavaScript errors
- Ensure data is selected (country + product)

### Heroku Deployment Issues

**Application error on Heroku:**
- Check logs: `heroku logs --tail`
- Verify Procfile configuration
- Ensure all dependencies are in requirements.txt

**Build fails:**
- Check Python version compatibility in runtime.txt
- Verify all packages in requirements.txt are available on PyPI

**Timeout errors:**
- Bokeh apps may take longer to load on Heroku's free tier
- Consider upgrading to a paid dyno for better performance

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.

## Contact

For questions or issues, please open an issue on the repository.

## Acknowledgments

- US Census Bureau for providing the International Trade API
- flagcdn.com for country flag images
- Bokeh project for the visualization framework
