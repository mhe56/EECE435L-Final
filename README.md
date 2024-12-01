# Project: E-commerce Platform with User Authentication

## Overview
This project is an E-commerce platform built using Flask, providing functionalities like user registration, authentication, product inventory management, and review submissions. The application is split into multiple services for modularity:

- **Service 1**: Handles user registration, login, and wallet management.
- **Service 2**: Manages product inventory, including adding, updating, and deducting stock.
- **Service 3**: Handles product catalog operations.
- **Service 4**: Manages reviews, including submitting, updating, and deleting reviews.

The application uses JWT-based authentication to protect endpoints that require user identification, ensuring that sensitive data is secured.

## Installation
### Prerequisites
- Docker and Docker Compose

### Setup Steps
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <project-directory>
   ```

2. Build and run the application using Docker Compose:
   ```sh
   docker-compose build
   docker-compose up
   ```

### Running the Application
- The application is containerized, and each service runs within its own container. You can use tools like Postman to test the endpoints after running `docker-compose up`.

## Notes
- Make sure the virtual environment is active when running the tests.
- Use the same `SECRET_KEY` across services to ensure JWT tokens are compatible.



