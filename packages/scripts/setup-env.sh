#!/bin/bash

echo "Setting up environment variables..."

# Copy default environment files
cp .env.defaults packages/frontend/.env
cp .env.defaults packages/backend/.env

echo "Environment variables set up successfully."
echo "Frontend .env file created at packages/frontend/.env"
echo "Backend .env file created at packages/backend/.env" 