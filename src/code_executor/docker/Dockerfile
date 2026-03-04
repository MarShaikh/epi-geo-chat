FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir \
    matplotlib \
    seaborn \
    geopandas \
    rasterio \
    folium \
    numpy \
    pandas \
    xarray \
    shapely \
    pyproj

RUN mkdir -p /workspace/input /workspace/output

# Non-root user for security
RUN useradd -m sandbox
USER sandbox

WORKDIR /workspace
