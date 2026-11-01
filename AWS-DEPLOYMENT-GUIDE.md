# 🚀 SeQuenX Backend — AWS EC2 Free Tier Deployment Guide

This guide shows you how to deploy the **SeQuenX FastAPI Backend** to an **AWS EC2 Free Tier instance** so it runs **24/7 continuously without sleeping** (solving Render's 15-minute inactivity shutdown).

---

## 🌟 Why AWS EC2 Free Tier?

| Feature | Render (Free Tier) | AWS EC2 (Free Tier) |
|---|---|---|
| **Sleep / Spin Down** | ❌ Sleeps after 15 minutes of inactivity | ✅ **Never sleeps — 24/7 uptime** |
| **Cold Starts** | ❌ 30–50s delay after sleeping | ✅ **0s cold start — always instant** |
| **Free Hours** | 750 shared pool | ✅ **750 hours/month dedicated** (12 months) |
| **Control** | Locked PaaS container | ✅ Full root access, Docker, Nginx, SSL |
| **Custom Domain & SSL** | Slow renewal | ✅ Free Let's Encrypt SSL via Certbot |

---

## 📋 Prerequisites
- An active **AWS Account** ([aws.amazon.com/free](https://aws.amazon.com/free))
- Your Backend Git repo: `https://github.com/ebadmahar/SequenxBackend`

---

## 🛠️ Step 1: Launch an EC2 Free Tier Instance (5 Minutes)

1. Log in to the [AWS Management Console](https://console.aws.amazon.com/).
2. In the top search bar, type **EC2** and click **EC2**.
3. Click the orange button: **Launch Instance**.
4. Configure the instance with these settings:
   - **Name:** `sequenx-backend`
   - **Application and OS Images:** Select **Ubuntu** -> **Ubuntu Server 24.04 LTS (HVM)** *(Free tier eligible)*.
   - **Instance type:** Select **t2.micro** (1 vCPU, 1 GiB Memory) or **t3.micro** *(both are Free Tier eligible)*.
   - **Key pair (login):**
     - Click **Create new key pair**.
     - Name: `sequenx-key`.
     - Key pair type: `RSA`.
     - Private key format: `.pem` (for Mac/Linux/OpenSSH) or `.ppk` (for PuTTY).
     - Click **Create key pair** and download it safely.
   - **Network settings:**
     - Select **Create security group**.
     - ✅ Check **Allow SSH traffic from Anywhere** (`0.0.0.0/0`).
     - ✅ Check **Allow HTTP traffic from the internet** (port 80).
     - ✅ Check **Allow HTTPS traffic from the internet** (port 443).
   - **Configure storage:**
     - Change from 8 GiB to **20 GiB or 30 GiB** `gp3` *(up to 30 GiB is 100% Free Tier eligible)*.
5. Click **Launch Instance**.

---

## 📌 Step 2: Assign a Static Elastic IP (Prevents IP from changing)

By default, an EC2 public IP changes whenever you restart the instance. An **Elastic IP** is a permanent, static IP address that is **100% free** while attached to your running EC2 instance.

1. On the left EC2 sidebar, click **Network & Security** -> **Elastic IPs**.
2. Click **Allocate Elastic IP address** -> click **Allocate**.
3. Select your new Elastic IP -> click **Actions** -> **Associate Elastic IP address**.
4. In **Instance**, choose your `sequenx-backend` instance.
5. Click **Associate**.
6. Note down your **Elastic IP address** (e.g. `54.210.123.45`).

---

## 💻 Step 3: Connect to your EC2 Instance

### Option A: Via Browser (Fastest — No software required)
1. In the EC2 Console, select your `sequenx-backend` instance.
2. Click the **Connect** button at the top.
3. Keep default tab **EC2 Instance Connect** and click **Connect**.
4. A browser terminal will open directly inside your Ubuntu server!

### Option B: Via SSH from your Computer
```bash
chmod 400 sequenx-key.pem
ssh -i sequenx-key.pem ubuntu@<YOUR_ELASTIC_IP>
```

---

## 🚀 Step 4: Deploy the Backend with One Command

Once you are inside the Ubuntu server terminal:

```bash
# 1. Clone your backend repository
git clone https://github.com/ebadmahar/SequenxBackend.git app
cd app

# 2. Run the automated setup script
chmod +x setup-ec2.sh
./setup-ec2.sh
```

### What `setup-ec2.sh` does automatically:
- Installs Docker & Docker Compose
- Installs Nginx & Certbot
- Configures Nginx reverse proxy (Port 80/443 &rarr; Port 8000)
- Builds and runs the FastAPI container with auto-restart enabled
- Mounts persistent database (`app.db`) and uploaded files (`uploads/`)
- Checks the API health status

Once finished, test your API in any browser:
```
http://<YOUR_ELASTIC_IP>/
http://<YOUR_ELASTIC_IP>/docs
```

---

## 🌐 Step 5: Connecting Your Custom Domain & Free SSL (Let's Encrypt)

> ⚠️ **Important: Why HTTPS / SSL is required**
> Your frontend runs on Netlify with HTTPS (`https://sequenxx.ebadmahar.site`).
> Web browsers **block** requests from `https://` websites to plain `http://` APIs (Mixed Content policy). Therefore, your backend **must have HTTPS** so Netlify can communicate with it!

### How to connect your domain:
Let's say you want your backend on `api.ebadmahar.site` (or any domain you own):

1. **Add a DNS Record in your Domain Registrar (Namecheap, Cloudflare, GoDaddy, Hostinger, etc.):**
   - **Type:** `A`
   - **Host / Name:** `api` (or `backend` or `@` for root)
   - **Value / Target:** `<YOUR_ELASTIC_IP>` (e.g. `54.210.123.45`)
   - **TTL:** Automatic or 1 minute

2. **Wait 1–2 minutes for DNS to propagate.** You can verify by opening your computer's terminal:
   ```bash
   ping api.yourdomain.com
   ```
   It should return your EC2 Elastic IP.

3. **SSH into your EC2 server and run Certbot:**
   ```bash
   sudo certbot --nginx -d api.yourdomain.com
   ```
   - Enter your email address.
   - Agree to terms (`y`).
   - Certbot will automatically verify the domain, generate a free Let's Encrypt SSL certificate, and configure Nginx!

4. **Verify HTTPS in your browser:**
   ```
   https://api.yourdomain.com/docs
   ```
   You now have a secure, green padlock HTTPS backend!

---

## 🔗 Step 6: Connect Netlify Frontend to your AWS Backend

1. Go to your [Netlify Dashboard](https://app.netlify.com/).
2. Select your site (`sequenxx.ebadmahar.site`).
3. Navigate to **Site configuration** -> **Environment variables**.
4. Add or update:
   - **Key:** `NEXT_PUBLIC_API_URL` (or `VITE_API_URL`)
   - **Value:** `https://api.yourdomain.com`
5. Go to **Deploys** -> click **Trigger deploy** -> **Clear cache and deploy site**.

Your frontend is now live on Netlify talking directly to your 24/7 AWS EC2 backend with zero sleep time!

---

## 💡 What if you don't have a domain yet? (Instant Free SSL)

If you haven't bought a domain yet, you can use **sslip.io** for instant free SSL:
Every IP address has a free wildcard domain that resolves to itself:
`<YOUR_ELASTIC_IP>.sslip.io` (for example: `54-210-123-45.sslip.io`)

You can run Certbot on it immediately:
```bash
sudo certbot --nginx -d 54-210-123-45.sslip.io
```
And use `https://54-210-123-45.sslip.io` in Netlify until you purchase your custom domain!

---

## 🔄 Useful Maintenance Commands on EC2

```bash
# View backend real-time logs
sudo docker compose logs -f

# Restart backend
sudo docker compose restart

# Pull latest code from GitHub and rebuild
git pull
sudo docker compose up -d --build

# Check Nginx status
sudo systemctl status nginx
```
