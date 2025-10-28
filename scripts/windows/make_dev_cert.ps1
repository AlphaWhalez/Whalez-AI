# Creates ./certs/cert.pem and ./certs/key.pem for local HTTPS
param(
  [string]$CertDir = "certs",
  [string]$CommonName = "localhost"
)

if (!(Test-Path $CertDir)) { New-Item -ItemType Directory -Path $CertDir | Out-Null }

# Requires OpenSSL in PATH. If missing, install openssl-light or use Git Bash's openssl.
$certPem = Join-Path $CertDir "cert.pem"
$keyPem  = Join-Path $CertDir "key.pem"

# Create self-signed cert valid 365 days
openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
  -keyout $keyPem -out $certPem `
  -subj "/C=US/ST=NA/L=Local/O=Whalez-AI/OU=Dev/CN=$CommonName"

Write-Host "[+] Wrote $certPem and $keyPem"
Write-Host "    Add to .env:"
Write-Host "    SSL_CERT=$certPem"
Write-Host "    SSL_KEY=$keyPem"
