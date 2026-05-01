#!/usr/bin/env bash
# Full deployment script for UPOU Admissions AI Helpdesk.
# Run from the project root: bash deploy.sh
#
# Prerequisites:
#   - AWS credentials exported (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN)
#   - terraform, npm, python3, zip installed
#   - infrastructure/terraform/terraform.tfvars configured

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================"
echo " UPOU Admissions AI Helpdesk — Deploy"
echo "============================================"

# ── Step 2: Package Lambda ────────────────────────────────────────────────────
echo ""
echo "==> [Step 2] Packaging Lambda..."
cd "$SCRIPT_DIR/backend/lambda"
bash package_clean.sh

# ── Step 3: Terraform Phase 1 (backend + API) ────────────────────────────────
echo ""
echo "==> [Step 3] Running Terraform Phase 1 (init + apply)..."
cd "$SCRIPT_DIR/infrastructure/terraform"
terraform init -input=false
terraform apply -auto-approve

# Extract API URL from Terraform output
API_URL=$(terraform output -raw api_url)
echo ""
echo "    API URL: $API_URL"

# ── Step 4: Frontend build ────────────────────────────────────────────────────
echo ""
echo "==> [Step 4] Configuring and building frontend..."
cd "$SCRIPT_DIR/frontend"
echo "VITE_API_URL=$API_URL" > .env
npm install
npm run build

# ── Step 5: Terraform Phase 2 (redeploy EC2 with new frontend) ───────────────
echo ""
echo "==> [Step 5] Running Terraform Phase 2 (taint EC2 + apply)..."
cd "$SCRIPT_DIR/infrastructure/terraform"
terraform taint aws_instance.frontend
terraform apply -auto-approve

# ── Step 6: Print access URL ──────────────────────────────────────────────────
EC2_IP=$(terraform output -raw ec2_public_ip)
echo ""
echo "============================================"
echo " Deployment complete!"
echo " App:     http://$EC2_IP"
echo " API URL: $API_URL"
echo "============================================"
