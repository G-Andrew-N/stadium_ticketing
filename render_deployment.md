# Render Deployment Guide

## 1. Project Preparation
- Ensure `.gitignore` excludes sensitive files (already done).
- Add a `requirements.txt` with all dependencies (already present).
- Add a `render.yaml` for Render deployment configuration.
- Add a `Procfile` to specify the web process.
- Ensure static and media files are handled (use WhiteNoise for static, Render's persistent disk for media).

## 2. Required Files

### render.yaml
```
services:
  - type: web
    name: stadium-ticketing
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn stadium_ticketing.wsgi:application"
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: stadium_ticketing.settings
      - key: SECRET_KEY
        value: <your-secret-key>
      - key: DEBUG
        value: False
    autoDeploy: true
```

### Procfile
```
web: gunicorn stadium_ticketing.wsgi:application
```

## 3. Static & Media Files
- Install WhiteNoise: `pip install whitenoise`
- Add to `requirements.txt`.
- Update `stadium_ticketing/settings.py`:
  - Add `'whitenoise.middleware.WhiteNoiseMiddleware'` to `MIDDLEWARE`.
  - Set `STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')`
  - Set `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')`
  - Set `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
- Run `python manage.py collectstatic` before deploying.

## 4. Database
- Use SQLite for demo/testing, but for production use Render's PostgreSQL add-on.
- Update `settings.py` for PostgreSQL if needed.

## 5. Deployment Steps
1. Commit all changes and push to GitHub.
2. Create a new Web Service on Render, connect your repo.
3. Add environment variables (SECRET_KEY, DEBUG, etc.).
4. Deploy and monitor logs for errors.

## 6. Useful Links
- Render Django docs: https://render.com/docs/deploy-django
- WhiteNoise docs: https://whitenoise.readthedocs.io/en/latest/

## 7. Troubleshooting
- Check logs for errors.
- Ensure all environment variables are set.
- Run migrations: `python manage.py migrate` (can be done via Render shell).
- For media uploads, use Render's persistent disk or S3.

---

**Summary:**
- Add `render.yaml` and `Procfile`.
- Use WhiteNoise for static files.
- Push to GitHub and connect to Render.
- Set environment variables and deploy.
