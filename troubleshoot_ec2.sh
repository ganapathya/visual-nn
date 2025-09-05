#!/bin/bash
# Troubleshooting script for Visual-NN on EC2

echo "🔍 Visual-NN EC2 Troubleshooting"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}📊 System Status${NC}"
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h /
echo ""

echo -e "${YELLOW}🔌 Service Status${NC}"
echo "Flask service:"
systemctl status visual-nn --no-pager -l
echo ""
echo "Nginx service:"
systemctl status nginx --no-pager -l
echo ""

echo -e "${YELLOW}🌐 Network Status${NC}"
echo "Ports listening:"
netstat -tlnp | grep -E ':(80|5001)'
echo ""

echo -e "${YELLOW}📝 Recent Logs${NC}"
echo "Flask logs (last 20 lines):"
journalctl -u visual-nn -n 20 --no-pager
echo ""
echo "Nginx error logs (last 10 lines):"
tail -n 10 /var/log/nginx/error.log 2>/dev/null || echo "No nginx error logs found"
echo ""

echo -e "${YELLOW}🧪 Endpoint Tests${NC}"
echo "Testing Flask directly:"
curl -s http://localhost:5001/health || echo "Flask not responding"
echo ""
echo "Testing via Nginx:"
curl -s http://localhost/api/health || echo "Nginx proxy not working"
echo ""

echo -e "${YELLOW}🔑 Configuration Check${NC}"
echo "Environment file:"
if [ -f "/opt/visual-nn/.env" ]; then
    echo "✅ .env file exists"
    grep -v "GEMINI_API_KEY" /opt/visual-nn/.env || echo "No config found"
    if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" /opt/visual-nn/.env; then
        echo -e "${YELLOW}⚠️ Default API key detected - AI features disabled${NC}"
    else
        echo -e "${GREEN}✅ Custom API key configured${NC}"
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
fi
echo ""

echo -e "${YELLOW}💾 Memory Analysis${NC}"
echo "Python processes:"
ps aux | grep python | grep -v grep
echo ""

echo -e "${YELLOW}🔧 Quick Fixes${NC}"
echo "To restart services:"
echo "  sudo systemctl restart visual-nn"
echo "  sudo systemctl restart nginx"
echo ""
echo "To view live logs:"
echo "  sudo journalctl -u visual-nn -f"
echo ""
echo "To test endpoints:"
echo "  curl http://localhost:5001/health"
echo "  curl http://localhost/api/health"
echo ""

# Get EC2 IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null)
if [ -n "$EC2_IP" ]; then
    echo "🌐 External Access:"
    echo "  http://$EC2_IP"
    echo "  http://$EC2_IP/api/health"
fi
