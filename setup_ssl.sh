#!/usr/bin/env bash
# Run this script on the EC2 instance to install and configure an SSL certificate.
# Usage: bash setup_ssl.sh <domain> <email>
# Example: bash setup_ssl.sh project.nbdona.is215.upou.io nbdona@up.edu.ph

set -euo pipefail

DOMAIN="${1:?Usage: $0 <domain> <email>}"
EMAIL="${2:?Usage: $0 <domain> <email>}"

echo "==> [1/6] Enabling EPEL repo..."
sudo amazon-linux-extras install epel -y

echo "==> [2/6] Installing certbot via pip (pinned for Python 3.7 + OpenSSL 1.0.2)..."
sudo pip3 install \
  "urllib3<2.0" \
  "certbot==1.32.0" \
  "certbot-nginx==1.32.0" \
  "acme==1.32.0"

echo "==> [3/6] Requesting SSL certificate from Let's Encrypt..."
sudo /usr/local/bin/certbot --nginx \
  -d "$DOMAIN" \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  --non-interactive || true

echo "==> [4/6] Adding server_name to Nginx config (if not already set)..."
NGINX_CONF="/etc/nginx/nginx.conf"
if ! grep -q "server_name.*$DOMAIN" "$NGINX_CONF"; then
  sudo sed -i "s|server_name\s*_;|server_name $DOMAIN;|g" "$NGINX_CONF"
  echo "    server_name set to $DOMAIN"
else
  echo "    server_name already set, skipping"
fi

echo "==> [5/6] Installing certificate into Nginx..."
sudo /usr/local/bin/certbot install \
  --cert-name "$DOMAIN" \
  --nginx \
  --non-interactive

echo "==> [6/6] Restarting Nginx..."
sudo systemctl restart nginx

echo ""
echo "Done. Your site should now be accessible at https://$DOMAIN"
echo "Certificate expires: $(sudo /usr/local/bin/certbot certificates 2>/dev/null | grep 'Expiry Date' | head -1 | awk '{print $3, $4}')"
