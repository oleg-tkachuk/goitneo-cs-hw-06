FROM python:3.12

WORKDIR /app

RUN adduser --disabled-password --no-create-home --gecos 'Non-privileged application user' appuser

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt \
&& chown -R appuser:appuser /app \
&& find /app -type d -exec chmod -v 550 {} \; \
&& find /app -type f -exec chmod -v 440 {} \;

USER appuser

CMD ["python", "main.py"]
