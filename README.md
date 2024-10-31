# WFH Scheduler Application

A Work From Home scheduling system that allows staff members to submit WFH requests, managers to approve/reject requests, and provides schedule visibility across teams.

You can access the cloud-hosted version of this application at [https://spm-wfh-scheduler.vercel.app/](https://spm-wfh-scheduler.vercel.app/)


## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
  - [Start Backend Server](#start-backend-server)
  - [Start Frontend Development Server](#start-frontend-development-server)
- [Test Users](#test-users)
- [CI/CD Pipeline](#cicd-pipeline)


## Features
- Staff WFH request submission
- Manager approval/rejection workflow
- Team schedule visibility
- Department-wide schedule overview
- Automated request expiration
- Responsive web interface

## Prerequisites
- Python 3.10 or higher
- Node.js 20.x or higher
- MySQL Server

## Installation

### Database Setup
Create the database and tables using the provided SQL script in `backend/WFH-Schedule.sql`


### Backend Setup
Create a `.env` file at the root of the backend directory with the following content:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=wfh_scheduler
```


Install the required Python packages (Create a virtual environment if necessary):
```bash
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
```


### Frontend Setup
Create a `.env` file at the root of the frontend directory with the following content:

```
VITE_API_URL=http://localhost:5000
```


Install the required Node.js packages:

```bash
cd frontend
npm install
```


## Running the Application

### Start Backend Server
Run the following commands to start the backend server:

```bash
cd backend
python run.py
```


The backend server will start on `http://localhost:5000`.

### Start Frontend Development Server
Run the following commands to start the frontend development server:

```bash
cd frontend
npm run dev
```


The frontend development server will start on `http://localhost:5173`.

## Test Users

The following test users are available in the system:


- **Director Level**
  - Email: financedirector@test.com
  - Password: password

- **Manager Level**
  - Email: financemanager1@test.com
  - Password: password

- **Staff Level**
  - Email: financestaff1@test.com
  - Password: password

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment. The pipeline includes:

### Backend CI/CD
- Python 3.10 setup
- Dependencies installation and caching
- Flake8 linting
- Unit tests execution
- Automated deployment to Render

### Frontend CI/CD
- Node.js 20.x setup
- Dependencies installation and caching
- Security audit
- Build verification
- Unit tests execution
- Automated deployment to Vercel

### Error Notification
- Automated error notifications via Telegram
- AI-powered error summarization using Groq
- Detailed error logs and build status reporting

### Pipeline Triggers
- Activated on push to main branch
- Sequential job execution
- Conditional deployment based on test success

The complete pipeline configuration can be found in `.github/workflows/main.yml`.

