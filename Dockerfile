FROM python:3.12-slim

# System dependencies for GDAL/rasterio (needed by geospatial libraries)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Azure CLI (needed for DefaultAzureCredential to authenticate with GeoCatalog)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg lsb-release && \
    curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (cache-friendly layer ordering)
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements/base.txt

# Copy application source and data files
COPY src/ src/
COPY code_samples/ code_samples/
COPY config/ config/
COPY docs/ docs/
COPY pyproject.toml .

# Install the project itself (so `src` is importable)
RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
