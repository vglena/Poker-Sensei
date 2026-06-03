FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

RUN useradd -m -u 1000 user

WORKDIR /home/user/app

COPY --chown=user app/backend/requirements.txt app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r app/backend/requirements.txt

COPY --chown=user agent agent
COPY --chown=user app app

USER user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", "--app-dir", "app/backend"]