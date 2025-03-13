# expenseswebsite

Project Description: Django Income-Expense Management Website
Overview
This is a web application designed to manage and track income and expenses. 
It allows users to Add and categorize income and expenses.
Generate detailed reports.
Export data in PDF format ,CSV Format and Excel Format for better analysis and record-keeping.
Built using the Django framework, this project ensures a robust and scalable backend with a clean and responsive frontend.

Key Features
User Authentication:

Secure login and registration.
User-specific data to ensure privacy.
Forgotten Password Through Real tie email
Registration success message through email

Income and Expense Tracking:

Add, edit, or delete income and expense entries.
Categorize entries for better organization.
Report Generation:

View reports summarizing financial data.
Export reports .
PDF Export:
CSV Export:
Excel Format:

Use WeasyPrint to generate well-formatted PDFs with customizable content.
Include images, such as the company logo, in exported PDFs.
Responsive Design:

Optimized for both desktop and mobile devices.

Technical Details
Backend:

Framework: Django 3.x
Database: PostgreSQL 

Frontend:

HTML, CSS, and Django Templates.

Static files are managed using Django's static file system.

Dependencies:

Django: The core framework for the application.
six: A compatibility library for smooth Python version handling.
WeasyPrint: For generating PDF reports.

Static Files:

Images (e.g., logo) and CSS styles are served via Django’s static module.
