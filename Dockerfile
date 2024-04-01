FROM python

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]

HEALTHCHECK CMD curl --fail "http://localhost:80/api_health" || exit 1
