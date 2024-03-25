FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY pyproject.toml poetry.lock /app

# Install any needed packages specified in pyproject.toml
RUN pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY *.py /app

ENTRYPOINT ["poetry", "run", "python3"]
CMD ["run.py"]
