# starting image
FROM python:3.14-slim

# define working directory
WORKDIR /app

# read and install libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy code
COPY py/ .

# run tests
CMD ["pytest", "-q"]