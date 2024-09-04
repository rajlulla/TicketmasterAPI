Here's a basic `README.md` file for your project:

# Ticketmaster API Dockerized Service

This service is a Dockerized FastAPI application that provides three API endpoints to interact with Ticketmaster. It leverages Puppeteer to extract cookies and intercept specific URLs for ticket price queries. The application is designed to be flexible for use in serverless or containerized environments like AWS Lambda or Kubernetes.

## Features

- **Initial Setup**: Fetches cookies and modifies the "quickpicks" URL based on the event URL and max price.
- **Get Cookies**: Fetches cookies for a specific Ticketmaster event.
- **Proxy Request**: Acts as a proxy to forward requests with specific headers and cookies to Ticketmaster's API.

## Installation and Running

### Prerequisites

- Docker installed on your machine

### Build and Run the Docker Container

1. Clone the repository.
2. Build the Docker image:
   ```bash
   docker build -t ticketmaster-api .
   ```
3. Run the Docker container:
   ```bash
   docker run -d -p 6131:6131 ticketmaster-api
   ```

### Required System Dependencies

The Docker container requires the following system dependencies to run Puppeteer:
- gconf-service, libasound2, libatk1.0-0, libatk-bridge2.0-0, libc6, libcairo2, libcups2, libdbus-1-3, libexpat1, libfontconfig1, libgcc1, libgconf-2-4, libgdk-pixbuf2.0-0, libglib2.0-0, libgtk-3-0, libnspr4, libpango-1.0-0, libpangocairo-1.0-0, libstdc++6, libx11-6, libx11-xcb1, libxcb1, libxcomposite1, libxcursor1, libxdamage1, libxext6, libxfixes3, libxi6, libxrandr2, libxrender1, libxss1, libxtst6, ca-certificates, fonts-liberation, libappindicator1, libnss3, lsb-release, xdg-utils, wget, libcairo-gobject2, libxinerama1, libgtk2.0-0, libpangoft2-1.0-0, libthai0, libpixman-1-0, libxcb-render0, libharfbuzz0b, libdatrie1, libgraphite2-3, libgbm1

These are installed in the Docker container during the build process.

## API Endpoints

### 1. Initial Setup

**Endpoint**: `/initial-setup`

**Method**: `POST`

**Request Body**:
```json
{
  "event_url": "<event_url>",
  "max_price": <maximum_price>
}
```

**Response**:
```json
{
  "cookie": "<cookie_string>",
  "quickpicks_url": "<modified_quickpicks_url>"
}
```

**Description**:
This endpoint takes in an event URL and a maximum price. It returns both the cookies and the modified "quickpicks" URL for ticket prices.

---

### 2. Get Cookies

**Endpoint**: `/get-cookies`

**Method**: `POST`

**Request Body**:
```json
{
  "event_url": "<event_url>"
}
```

**Response**:
```json
{
  "cookie": "<cookie_string>"
}
```

**Description**:
This endpoint fetches the cookies for a specific Ticketmaster event based on the provided event URL. The `quickpicks` URL is not intercepted.

---

### 3. Proxy Request

**Endpoint**: `/proxy`

**Method**: `POST`

**Request Body**:
```json
{
  "quickpicks_url": "<quickpicks_url>",
  "cookie": "<cookie_string>"
}
```

**Response**:
Returns the response from the Ticketmaster API.

**Description**:
Acts as a proxy, forwarding the `quickpicks_url` and the associated cookies to Ticketmaster's API, and returns the response from the API.

---

## Authentication

All API requests must include an `x-api-key` header for authentication.

**Example Header**:
```json
{
  "x-api-key": "your-secret-api-key"
}
```

---

## License

MIT License

---

## Contact

For further inquiries, feel free to reach out.
```

### Instructions:

1. Replace `"your-secret-api-key"` with your actual API key.
2. Modify the contact section to suit your preferred contact information (email, GitHub link, etc.).

This `README.md` provides a clear overview of the application and the API endpoints for users.
