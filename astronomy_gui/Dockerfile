FROM python:3.8-alpine
LABEL maintainer='christopher.anthony@libertymutual.com'

# Copy application files into container
COPY * /app/

# Install Flask and requests
RUN pip3 install Flask
RUN pip3 install requests
# Install curl
RUN apk add curl
 
# Have the container expose port 8080
EXPOSE 8080

# Have the app run as a non-root user
USER 1001

# Run healthcheck
HEALTHCHECK --interval=5m --timeout=3s \
  CMD curl -f http://localhost:8080/ || exit 1

CMD python3 /app/solar_app.py
