#!/bin/bash

# Create deployment directory
mkdir -p deployment/static/css
mkdir -p deployment/static/js
mkdir -p deployment/templates

# Copy main Python files
cp app.py deployment/
cp main.py deployment/
cp wsgi.py deployment/
cp data.json deployment/
cp pythonanywhere_requirements.txt deployment/requirements.txt

# Copy static files
cp static/css/style.css deployment/static/css/
cp static/js/main.js deployment/static/js/

# Copy templates
cp templates/*.html deployment/templates/

# Copy documentation
cp README.md deployment/
cp DEPLOYMENT_GUIDE.md deployment/

# Create a zip file for easy download
cd deployment
zip -r ../gifts4u_deployment.zip *
cd ..

echo "Deployment package created: gifts4u_deployment.zip"
echo "You can download this file and upload it to PythonAnywhere"