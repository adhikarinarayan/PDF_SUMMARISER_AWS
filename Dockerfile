# Phase 1: Use Google's mirror for Python slim image
FROM mirror.gcr.io/library/python:3.11-slim-bookworm

# Phase 2: Set working directory
WORKDIR /app

# Phase 3: Copy dependency lists into the container
# We copy only the requirements file first to leverage Docker's layer caching.
# If requirements.txt doesn't change, Docker won't re-run the package installation step.
COPY requirements.txt .

# Phase 4: Install dependencies using uv
# We install uv and then use it to install the packages from requirements.txt.
# --no-cache-dir reduces the final image size.
RUN pip install uv && \
    uv pip install --no-cache-dir --system -r requirements.txt

# Phase 5: Copy application code (excluding .env via .dockerignore)
COPY . .

# Phase 6: Expose port
EXPOSE 5000

# Phase 7: Define the command to run the application
CMD ["python", "app.py"]