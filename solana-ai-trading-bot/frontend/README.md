# Solana AI Trading Bot - Frontend

This directory contains the React.js frontend application for the Solana AI Trading Bot. It provides a web interface for monitoring bot activity, viewing trading data, managing settings, and interacting with the reputation database.

## Technologies Used

- **React.js**: A JavaScript library for building user interfaces.
- **Tailwind CSS**: A utility-first CSS framework for rapidly building custom designs.
- **Headless UI**: Completely unstyled, fully accessible UI components, designed to integrate beautifully with Tailwind CSS.
- **React Router DOM**: For declarative routing in React applications.
- **Solana Web3.js & Wallet Adapters**: For potential future direct interaction with Solana blockchain from the frontend (e.g., displaying wallet balance, transaction history).

## Project Structure

- `public/`: Contains static assets like `index.html`, `favicon.ico`, and manifest files.
- `src/`: Contains the main React application source code.
  - `components/`: Reusable React components (e.g., `Dashboard.js`, `Login.js`, `PrivateRoute.js`).
  - `App.js`: The main application component, setting up routing.
  - `index.js`: The entry point of the React application.
  - `App.css`, `index.css`: Tailwind CSS imports and global styles.
  - `reportWebVitals.js`: For measuring performance.
  - `setupTests.js`: For test setup.

## Available Scripts

In the project directory, you can run:

- `yarn start`: Runs the app in development mode.
- `yarn build`: Builds the app for production to the `build` folder.
- `yarn test`: Launches the test runner.
- `yarn eject`: Removes the single build dependency from your project.

## Deployment

The frontend is designed to be built and served as static files by the FastAPI backend. The `Dockerfile` in the root directory handles the build process of this frontend application and serves it.