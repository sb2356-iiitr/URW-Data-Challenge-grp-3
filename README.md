# URW Data Challenge - Group 3: AI-Driven Tenant Mix Optimizer

**Group 3:** A. Arya, S. Bairagi, S. Capizzi, L. Passet, I. Sijelmassi, J. Xu

## Executive Summary
This project aims to optimize the tenant mix for Unibail-Rodamco-Westfield (URW) shopping centers. By leveraging AI and data analytics, we identify underperforming assets and recommend optimal tenant sub-categories to maximize revenue uplift and sales density.

## Project Overview
Our solution provides a data-driven approach to leasing relations, offering an "AI-Driven Tenant Mix Optimizer" dashboard. This tool allows URW teams to:
*   **Visualize** current mall performance and store metrics.
*   **Identify** underperforming stores based on sales density and other key indicators.
*   **Simulate** the impact of replacing current tenants with AI-recommended categories.
*   **Estimate** potential revenue unlock and density uplift.

## Repository Structure

The repository contains the following key components:

### Dashboard Application
*   `app.py`: The main Streamlit application file. This runs the "URW Retail Mix Optimizer" dashboard, providing an interactive interface for mall analysis and scenario simulation.

### Data Analysis & Modeling Notebooks
*   `EDA_Iliass.ipynb` & `EDA_Lydia.ipynb`: Notebooks for Exploratory Data Analysis, understanding the data distribution, and identifying initial patterns.
*   `Feature_Engineering.ipynb`: Processes raw data to create relevant features for the machine learning models.
*   `Feature_Importance.ipynb`: Analyzes which features have the most significant impact on the model's predictions.
*   `Model.ipynb`: The core modeling notebook that trains the recommendation engine. Running the final section of this notebook generates the necessary data file (`urw_dashboard_data.csv`) for the dashboard.
*   `Model_Comparison.ipynb`: Compares different modeling approaches to select the best performer.


## Usage Instructions

### Prerequisites
Ensure you have Python installed along with the following libraries:
*   streamlit
*   pandas
*   altair
*   numpy

You can install them using pip:
```bash
pip install streamlit pandas altair numpy
```

### Running the Dashboard
1.  Navigate to the repository folder in your terminal.
2.  Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```
3.   The dashboard will open in your default web browser.

### Note on Data
If the `urw_dashboard_data.csv` file is missing, the dashboard will show an error. Please run the `Feature_Engineering.ipynb` and `Model.ipynb` notebooks (specifically the final section) to generate this file before running the app.

