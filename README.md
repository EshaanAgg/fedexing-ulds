# FedEx - Inter IIT Tech Meet 13.0

This project aims to solve the complex problem of optimizing the packing of packages into Unit Load Devices (ULDs), considering multiple constraints and optimization goals. By using a Genetic Algorithm with an innovative Octa-Branching placement strategy, the solution efficiently and stably packs items, improving overall logistics and operations.

## Key Features

### 1. **Constraint Handling**

- **Package and ULD Compatibility**: Ensures that the right packages fit in the right ULDs based on size, weight, and shape constraints.
- **Heavy and Fragile Package Considerations**: Takes into account the special handling required for heavy and fragile items, ensuring their safe placement.
- **Priority and Non-Priority Package Differentiation**: Differentiates between priority and non-priority packages, optimizing the placement based on urgency.

### 2. **Stability Optimization**

- **Moment Stabilization**: Implements moment stabilization techniques to ensure the packages' stability inside the ULD, preventing shifts during transit.
- **Structural and Physical Stability Metrics**: Uses metrics that measure and enhance the physical stability of the packing arrangement, ensuring no structural compromise.

### 3. **Efficient Placement**

- **Octa-Branching Placement Strategy**: A novel strategy that uses a rapid exploration of the solution space, optimizing placement speed and accuracy.

### 4. **Loading Plan Generation**

- **Topological Sorting for Efficient Loading Sequence**: Generates a highly optimized loading sequence based on topological sorting, ensuring the most efficient loading order.

### 5. **User-Friendly Interface**

- **Web-Based Dashboard**: A visually rich interface for input, real-time visualization, and export options for your optimized loading plans.

## Project Structure

The project consists of three main folders:

- **python_server**: A Python-based server that implements the core solution.
- **rust_server**: A Rust-based server, written later for better performance and speed, offering the same solution as `python_server`.
- **viz**: The front-end visualization part of the project, used for presenting the optimized packing plans.

You need to run the frontend from the [viz](viz) folder, and the backend from either the [python_server](python_server) or [rust_server](rust_server) folder, based on what you prefer.

## Getting Started

### Prerequisites

Ensure that you have the following installed on your system:

- Docker (for running rust_server)
- `Node.js` and `npm` (for running the frontend)
- Python (for running the Python server)

### Running the Rust Server

To run the `rust_server`, follow these steps:

1. Navigate to the `rust_server` folder:

   ```bash
   cd rust_server
   ```

2. Build the Docker image:

   ```bash
   docker build -t rust_server .
   ```

3. Run the Docker container:

   ```bash
   docker run -p 8000:8000 rust_server
   ```

   The server will be accessible at `http://localhost:8000`.

### Running the Visualization (viz)

To run the front-end visualization:

1. Navigate to the `viz` folder:

   ```bash
   cd viz
   ```

2. Install the required dependencies:

   ```bash
   npm install
   ```

3. Rename `sample.env` to `.env`:

   ```bash
   mv sample.env .env
   ```

4. Start the development server:

   ```bash
   npm run dev
   ```

   The visualization will be available at `http://localhost:3000`.

### Running the Python Server

To run the Python server, follow these steps:

1. Navigate to the `python_server` folder:

   ```bash
   cd python_server
   ```

2. Build the Docker image:

   ```bash
   docker build -t python_server .
   ```

3. Run the Docker container:

   ```bash
   docker run -p 8000:8000 python_server
   ```

The server will be accessible at `http://localhost:8000`.

