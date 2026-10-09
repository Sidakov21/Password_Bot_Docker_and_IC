FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends fontconfig \
    && rm -rf /var/lib/apt/lists/*

COPY Task_2_Bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Task_2_Bot/ .

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "bot.main"]
