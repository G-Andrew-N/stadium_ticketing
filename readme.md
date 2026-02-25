# Stadium Ticketing System

## Overview
This is a Django-based web application for managing stadium events and ticketing. The system allows event organizers to create and manage events, users to register and purchase tickets, and admins to oversee all activities. It is designed for both desktop and mobile use, with a focus on responsive UI and clear workflows.

## Features
- Event creation and management
- Ticket type selection and purchase
- User registration, login, and profile management
- Admin dashboard for event and user oversight
- QR code generation for tickets
- Media uploads for event thumbnails and user profiles
- Persistent footer and responsive layout

## How It Works
1. **Event Management**: Organizers can create, edit, and delete events. Each event can have multiple ticket types, prices, and quantities.
2. **Ticketing**: Users can view events, select ticket types, and purchase tickets. Purchased tickets are associated with user accounts and include QR codes for entry.
3. **User Accounts**: Users can register, log in, reset passwords, and edit profiles. Admins have access to additional controls via the admin dashboard.
4. **Admin Dashboard**: Admins can view all events, users, and tickets, manage event details, and monitor ticket sales.
5. **Media & Static Files**: Event thumbnails, profile photos, and ticket QR codes are stored in the media directory. Static files (CSS, images) are used for UI styling.

## Project Structure
- `events/`: Event management (models, views, templates)
- `tickets/`: Ticketing logic (models, views, templates)
- `users/`: User authentication and profiles
- `stadium_ticketing/`: Project settings, URLs, and base templates
- `media/`: Uploaded files (thumbnails, profiles, QR codes)
- `static/`: Static assets (CSS, images)

## Setup
1. Clone the repository.
2. Create a virtual environment and install dependencies from `requirements.txt`.
3. Run migrations to set up the database.
4. Start the development server with `python manage.py runserver`.


## License
This project is a demo to be iterated later
