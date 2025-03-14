# RESTful API for E-Commerce Platform

## Objective
Develop a production-grade RESTful API for a simple e-commerce platform. This platform allows users to view available products, add new products, and place orders. The solution includes exception handling, comprehensive test cases, and a Dockerized container for easy deployment.

## Features
- View available products
- Add new products
- Place orders with stock validation
- Order processing and inventory management
- Exception handling for errors like insufficient stock

## Technologies Used
- **Django Rest Framework (DRF)** for API development
- **SQLite** as the database
- **Docker & Docker Compose** for containerization
- **pytest** for testing

## Setup & Installation
### Prerequisites
Ensure you have the following installed:
- **Docker** & **Docker Compose**

### Running the Project
1. Clone the repository:
   ```sh
   git clone https://github.com/shenoy-dsouza/zania-store.git
   cd zania-store
   ```
2. Build and run the project using Docker:
   ```sh
   docker-compose up --build
   ```
3. The API will be available at:
   ```sh
   http://localhost:8000
   ```

## API Endpoints
| Method | Endpoint      | Description                   |
|--------|--------------|-------------------------------|
| GET    | `/products/`  | Retrieve all products        |
| POST   | `/products/`  | Add a new product            |
| POST   | `/orders/`    | Place an order               |

## Data Models
### Product
- `id`: Integer (unique)
- `name`: String
- `description`: String
- `price`: Float
- `stock`: Integer

### Order
- `id`: Integer (unique)
- `products`: List of product IDs and quantities
- `total_price`: Float
- `status`: String (e.g., "pending", "completed")

## Business Logic & Constraints
### Stock Management
- Validate stock levels when placing an order.
- Deduct stock if the order is successful.

### Order Validation
- Ensure sufficient stock is available before confirming an order.
- Return an appropriate error response if stock is insufficient.

## Testing
To run tests inside the Docker container:
```sh
docker-compose exec web pytest
```

## Environment Variables
Use a `.env` file to configure environment variables if needed. Example:
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## Dockerization
The application is fully containerized using Docker for easy deployment and scalability. The `Dockerfile` and `docker-compose.yml` handle dependencies and setup.

