# Stage 1
FROM python:3.9 AS builder

WORKDIR /usr/src/app

COPY . .

RUN python -m venv venv

SHELL [ "/bin/bash", "-c" ]
RUN source venv/bin/activate && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2
FROM python:3.9-slim
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/ /usr/src/app/
EXPOSE 8000
CMD ["/bin/bash", "-c", "source venv/bin/activate && exec python3 manage.py runserver 0.0.0.0:8000"]