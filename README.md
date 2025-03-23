# JS-Free Marketplace

A Python Flask-based marketplace application for cryptocurrency-related products. The application is designed to function without client-side JavaScript.

## Features

- User authentication (login/register)
- Product listings
- Shopping cart functionality
- Checkout process
- Order management
- Admin dashboard
- Vendor dashboard

## Project Structure

```
js-free-marketplace/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── config.py              # Configuration
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── login.html         # Login page
│   └── ...                # Other templates
└── static/                # Static assets (CSS, images)
```

## Local Development

1. Clone the repository
   ```
   git clone https://github.com/yourusername/js-free-marketplace.git
   cd js-free-marketplace
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Run the application
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Deployment Options

### Option 1: Deploy on Heroku

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku CLI
   ```
   heroku login
   ```

3. Create a new Heroku app
   ```
   heroku create your-app-name
   ```

4. Add PostgreSQL add-on
   ```
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. Set environment variables
   ```
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set FLASK_ENV=production
   ```

6. Create a Procfile with the following content:
   ```
   web: gunicorn app:app
   ```

7. Deploy to Heroku
   ```
   git push heroku main
   ```

8. Initialize the database
   ```
   heroku run python -c "from app import db; db.create_all()"
   ```

### Option 2: Deploy on AWS Elastic Beanstalk

1. Install the AWS CLI and EB CLI
2. Create an AWS account if you don't have one
3. Configure AWS CLI
   ```
   aws configure
   ```

4. Initialize EB application
   ```
   eb init -p python-3.8 js-free-marketplace
   ```

5. Create an environment
   ```
   eb create marketplace-env
   ```

6. Update environment variables
   ```
   eb setenv SECRET_KEY=your_secret_key FLASK_ENV=production
   ```

7. Deploy the application
   ```
   eb deploy
   ```

### Option 3: Deploy on DigitalOcean App Platform

1. Create a DigitalOcean account
2. Create a new App and connect your GitHub repository
3. Configure the environment:
   - Set the run command to: `gunicorn app:app`
   - Add environment variables: `SECRET_KEY`, `FLASK_ENV=production`
4. Deploy the application

### Option 4: Deploy on Google App Engine

1. Create a Google Cloud account
2. Install the Google Cloud SDK
3. Create an app.yaml file:
   ```
   runtime: python38

   env_variables:
     SECRET_KEY: "your_secret_key"
     FLASK_ENV: "production"

   handlers:
   - url: /.*
     script: auto
   ```

4. Deploy to App Engine
   ```
   gcloud app deploy
   ```

## Database Setup

This application uses PostgreSQL by default. Make sure to setup the database according to your deployment platform's requirements and update the `DATABASE_URL` environment variable.

## Environment Variables

- `SECRET_KEY`: Secret key for session encryption
- `DATABASE_URL`: Database connection string
- `FLASK_ENV`: Environment (development/production)
- `ADMIN_EMAIL`: Admin user email (for initial setup)
- `ADMIN_PASSWORD`: Admin user password (for initial setup)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
