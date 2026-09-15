FROM python:3.12-slim

WORKDIR /app
COPY hosted_server.py studio_hosted.html ./

# Environment
ENV PORT=8000
ENV DATA_DIR=/data
ENV PYTHONUNBUFFERED=1

# Health check endpoint for Coolify rolling updates
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/health').read()" || exit 1

# Persistent volume for surveys, sessions, images
VOLUME ["/data"]

EXPOSE ${PORT}

CMD ["python3", "hosted_server.py"]
