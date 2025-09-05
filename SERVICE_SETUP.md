# Visual Neural Network - Systemd Service Setup

This guide explains how to set up the Visual Neural Network Flask application as a systemd service on Ubuntu/Debian systems.

## Prerequisites

- Ubuntu/Debian system with Python 3.8+
- Root or sudo access
- Project files in `/home/ubuntu/visual-nn/`

## Quick Setup

1. **Clone or copy the project to the correct location:**
   ```bash
   sudo mkdir -p /home/ubuntu
   sudo chown ubuntu:ubuntu /home/ubuntu
   # Copy your project files to /home/ubuntu/visual-nn/
   ```

2. **Run the setup script:**
   ```bash
   sudo ./setup_service.sh
   ```

This script will:
- Create a Python virtual environment
- Install all dependencies (including gunicorn)
- Create and configure the systemd service
- Start the service automatically

## Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment
```bash
cd /home/ubuntu/visual-nn
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-light.txt
```

### 2. Create Systemd Service File
Copy the `visual-nn.service` file to `/etc/systemd/system/`:
```bash
sudo cp visual-nn.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/visual-nn.service
```

### 3. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable visual-nn.service
sudo systemctl start visual-nn.service
```

## Service Management

### Check Service Status
```bash
sudo systemctl status visual-nn
```

### Start/Stop/Restart Service
```bash
sudo systemctl start visual-nn
sudo systemctl stop visual-nn
sudo systemctl restart visual-nn
```

### View Logs
```bash
# View recent logs
sudo journalctl -u visual-nn --no-pager -n 50

# Follow logs in real-time
sudo journalctl -u visual-nn -f
```

### Disable Service
```bash
sudo systemctl disable visual-nn
```

## Troubleshooting

### Run the Troubleshooting Script
```bash
sudo ./troubleshoot_service.sh
```

### Common Issues and Solutions

#### 1. Service Fails to Start (Exit Code 203/EXEC)
**Problem:** The executable file doesn't exist or isn't executable.

**Solution:**
```bash
# Check if virtual environment exists
ls -la /home/ubuntu/visual-nn/venv/bin/gunicorn

# If missing, recreate virtual environment
cd /home/ubuntu/visual-nn
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-light.txt
```

#### 2. Permission Denied
**Problem:** Service can't access files or directories.

**Solution:**
```bash
# Set correct ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/visual-nn
sudo chmod +x /home/ubuntu/visual-nn/venv/bin/gunicorn
```

#### 3. Port Already in Use
**Problem:** Port 5001 is already occupied.

**Solution:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :5001

# Kill the process or change the port in visual-nn.service
```

#### 4. Missing Dependencies
**Problem:** Python packages not installed.

**Solution:**
```bash
cd /home/ubuntu/visual-nn
source venv/bin/activate
pip install -r requirements-light.txt
```

### Manual Testing

Test the application manually to isolate issues:

```bash
cd /home/ubuntu/visual-nn
source venv/bin/activate

# Test gunicorn
gunicorn --version

# Test the app
python app.py

# Test with gunicorn
gunicorn --workers 1 --bind 0.0.0.0:5001 app:app
```

## Configuration

### Service Configuration
The service file (`visual-nn.service`) contains:
- **Working Directory:** `/home/ubuntu/visual-nn`
- **User:** `ubuntu`
- **Port:** `5001`
- **Workers:** `4`
- **Environment:** `FLASK_ENV=production`

### Application Configuration
The application uses the configuration from `config.py`:
- Development mode: `FLASK_ENV=development`
- Production mode: `FLASK_ENV=production`

### Environment Variables
You can modify these in the service file:
- `FLASK_ENV`: Set to `production` for the service
- `PYTHONUNBUFFERED`: Set to `1` for better logging
- `PATH`: Points to the virtual environment

## Security Considerations

1. **Firewall:** Ensure port 5001 is open if accessing from external networks
2. **User Permissions:** The service runs as the `ubuntu` user
3. **File Permissions:** Ensure sensitive files are not world-readable
4. **HTTPS:** Consider using a reverse proxy (nginx) with SSL for production

## Monitoring

### Health Check
The application should respond to:
```
http://your-server-ip:5001/
```

### Log Monitoring
Monitor logs for errors:
```bash
sudo journalctl -u visual-nn -f | grep ERROR
```

### Resource Monitoring
Check resource usage:
```bash
# Check memory usage
ps aux | grep gunicorn

# Check disk space
df -h /home/ubuntu/visual-nn
```

## Backup and Recovery

### Backup Configuration
```bash
# Backup service configuration
sudo cp /etc/systemd/system/visual-nn.service /home/ubuntu/visual-nn/backup/

# Backup virtual environment (optional)
tar -czf venv_backup.tar.gz venv/
```

### Recovery
```bash
# Restore service configuration
sudo cp backup/visual-nn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart visual-nn
```

## Support

If you encounter issues:
1. Run the troubleshooting script: `sudo ./troubleshoot_service.sh`
2. Check the logs: `sudo journalctl -u visual-nn -f`
3. Test manually as described above
4. Verify all file paths and permissions
