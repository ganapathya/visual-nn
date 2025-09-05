# AWS Deployment Guide for Visual Neural Network

This guide will help you deploy the Visual Neural Network application to your AWS EC2 instance and fix the systemd service issue.

## Prerequisites

- AWS EC2 instance running Ubuntu/Debian
- SSH access to your instance
- Your SSH key file (`.pem` file)

## Step 1: Connect to Your AWS Instance

```bash
ssh -i /path/to/your-key.pem ubuntu@your-ec2-instance-ip
```

## Step 2: Prepare the Project Directory

```bash
# Create the project directory
sudo mkdir -p /home/ubuntu/visual-nn
sudo chown ubuntu:ubuntu /home/ubuntu/visual-nn
cd /home/ubuntu/visual-nn
```

## Step 3: Transfer Project Files

You have several options to transfer your project files:

### Option A: Using SCP (from your local machine)

```bash
# From your local machine, in the project directory:
scp -i /path/to/your-key.pem -r . ubuntu@your-ec2-instance-ip:/home/ubuntu/visual-nn/
```

### Option B: Using Git (if your project is in a repository)

```bash
# On the AWS instance:
cd /home/ubuntu/visual-nn
git clone https://github.com/your-username/visual-nn.git .
```

### Option C: Manual file transfer

Copy and paste the contents of these files:

- `app.py`
- `config.py`
- `requirements-light.txt`
- `requirements.txt`
- Any other project files

## Step 4: Create the Systemd Service Files

Create the service file on your AWS instance:

```bash
sudo nano /etc/systemd/system/visual-nn.service
```

Copy this content:

```ini
[Unit]
Description=Visual Neural Network Flask App
After=network.target

[Service]
Type=notify
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/visual-nn
Environment=PATH=/home/ubuntu/visual-nn/venv/bin
Environment=FLASK_ENV=production
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/ubuntu/visual-nn/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5001 --timeout 120 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=visual-nn

[Install]
WantedBy=multi-user.target
```

## Step 5: Set Up Virtual Environment and Dependencies

```bash
cd /home/ubuntu/visual-nn

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies (use requirements-light.txt for EC2)
pip install -r requirements-light.txt

# Verify gunicorn is installed
gunicorn --version
```

## Step 6: Set Up and Start the Service

```bash
# Set proper permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/visual-nn
chmod +x venv/bin/gunicorn

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable the service
sudo systemctl enable visual-nn.service

# Start the service
sudo systemctl start visual-nn.service

# Check status
sudo systemctl status visual-nn
```

## Step 7: Verify the Deployment

```bash
# Check if the service is running
sudo systemctl is-active visual-nn

# Check the logs
sudo journalctl -u visual-nn --no-pager -n 20

# Test the application
curl http://localhost:5001/
```

## Step 8: Configure Security Group

Make sure your EC2 security group allows inbound traffic on port 5001:

1. Go to AWS Console → EC2 → Security Groups
2. Select your instance's security group
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 5001
   - Source: 0.0.0.0/0 (or your IP for security)

## Troubleshooting

### If the service fails to start:

1. **Check the logs:**

   ```bash
   sudo journalctl -u visual-nn -f
   ```

2. **Verify file paths:**

   ```bash
   ls -la /home/ubuntu/visual-nn/venv/bin/gunicorn
   ls -la /home/ubuntu/visual-nn/app.py
   ```

3. **Test manually:**

   ```bash
   cd /home/ubuntu/visual-nn
   source venv/bin/activate
   gunicorn --workers 1 --bind 0.0.0.0:5001 app:app
   ```

4. **Check permissions:**
   ```bash
   sudo chown -R ubuntu:ubuntu /home/ubuntu/visual-nn
   chmod +x /home/ubuntu/visual-nn/venv/bin/gunicorn
   ```

### Common Issues:

1. **Exit code 203/EXEC**: Virtual environment or gunicorn not found

   ```bash
   # Recreate virtual environment
   cd /home/ubuntu/visual-nn
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements-light.txt
   ```

2. **Permission denied**: Fix ownership and permissions

   ```bash
   sudo chown -R ubuntu:ubuntu /home/ubuntu/visual-nn
   chmod +x /home/ubuntu/visual-nn/venv/bin/gunicorn
   ```

3. **Port already in use**: Check what's using port 5001
   ```bash
   sudo netstat -tlnp | grep :5001
   sudo lsof -i :5001
   ```

## Service Management Commands

```bash
# Start the service
sudo systemctl start visual-nn

# Stop the service
sudo systemctl stop visual-nn

# Restart the service
sudo systemctl restart visual-nn

# Check status
sudo systemctl status visual-nn

# View logs
sudo journalctl -u visual-nn -f

# Disable service (won't start on boot)
sudo systemctl disable visual-nn
```

## Access Your Application

Once everything is set up, your application will be available at:

```
http://your-ec2-instance-ip:5001
```

## Monitoring

```bash
# Monitor logs in real-time
sudo journalctl -u visual-nn -f

# Check resource usage
ps aux | grep gunicorn

# Check disk space
df -h /home/ubuntu/visual-nn
```

## Backup and Recovery

```bash
# Backup your configuration
sudo cp /etc/systemd/system/visual-nn.service /home/ubuntu/visual-nn/backup/

# Backup virtual environment (optional)
cd /home/ubuntu/visual-nn
tar -czf venv_backup.tar.gz venv/
```

This should resolve your systemd service issue and get your Visual Neural Network application running properly on your AWS instance!
