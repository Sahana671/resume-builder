# AWS Cloud Deployment Guide: AI Resume Screening System

This comprehensive, step-by-step guide is designed for developers with zero prior AWS cloud experience. By following this guide, you will transition the **AI Resume Screening System** from running on `localhost` to a live, production-grade cloud architecture on **Amazon Web Services (AWS)**.

---

## 1. Cloud Architecture Overview

The system uses dedicated, industry-standard AWS services for each layer:

```
[ Recruiter's Web Browser ]
             │
             ▼ (HTTPS)
   [ AWS Amplify Hosting ]  ── (Serves React + Vite Frontend)
             │
             ▼ (REST API / JSON)
      [ AWS EC2 Instance ]   ── (FastAPI Backend Server + Systemd 24/7)
        │            │
        │            ▼ (Read/Write SQL via Port 3306)
        │     [ Amazon RDS (MySQL) ] ── (Users, Jobs, Candidates, Scores)
        │
        ▼ (Uploads / Presigned URLs)
   [ Amazon S3 Bucket ]      ── (Secure PDF / DOCX Resume Storage)
```

| Layer | AWS Service | Role in the Project | Free Tier Allowance |
|---|---|---|---|
| **Frontend** | **AWS Amplify Hosting** | Hosts React (Vite) Single Page Application with automated HTTPS | 1,000 build minutes/month, 5 GB served/month |
| **Backend API** | **AWS EC2 (Ubuntu 24.04)** | Runs FastAPI application and NLP screening engine 24/7 | 750 hours/month of `t2.micro` or `t3.micro` |
| **Database** | **Amazon RDS (MySQL 8.0)** | Managed relational database for users, jobs, and scores | 750 hours/month of `db.t3.micro` or `db.t4g.micro` |
| **Object Storage** | **Amazon S3** | Secure, durable storage for uploaded candidate resumes | 5 GB of standard storage for 12 months |
| **Security & Auth** | **AWS IAM** | Secure API credentials for S3 bucket access | Always Free |

---

## 2. Prerequisites & Preparation

1. **Active AWS Account**: Sign up at [https://aws.amazon.com](https://aws.amazon.com) if you haven't already.
2. **Target AWS Region**: Pick one region close to you and keep it consistent across all services:
   * **Asia Pacific (Mumbai)**: `ap-south-1`
   * **US East (N. Virginia)**: `us-east-1`
   * **Europe (Frankfurt)**: `eu-central-1`
3. **Git Repository**: Your project repository on GitHub.

---

## Phase 1: Create Amazon S3 Bucket for Resumes

Amazon S3 will store the actual resume files (PDF, DOC, DOCX).

1. Log into the [AWS Management Console](https://console.aws.amazon.com/).
2. Select your chosen region in the top navigation bar (e.g., **ap-south-1**).
3. Search for **S3** in the top search bar and click on it.
4. Click the orange **Create bucket** button.
5. Configure the following:
   * **Bucket name**: Enter a unique name, e.g., `resume-screening-bucket-<yourname>-2026` *(must be lowercase, no spaces)*.
   * **AWS Region**: Match your selected region.
   * **Object Ownership**: ACLs disabled (recommended).
   * **Block Public Access settings**: Keep **Block all public access** checked. Resumes contain private PII; your backend will generate time-limited Presigned URLs for viewing them securely.
   * **Bucket Versioning**: Optional (Disable for lower storage usage).
   * **Default Encryption**: Server-side encryption with Amazon S3 managed keys (SSE-S3).
6. Click **Create bucket** at the bottom.
7. **Save your Bucket Name**: You will need it in `backend/.env`.

---

## Phase 2: Create an IAM User for S3 Access

Your backend running on EC2 needs an Access Key to upload files to your S3 bucket.

1. Search for **IAM** in the top AWS search bar and select it.
2. In the left menu, click **Users**, then click **Create user**.
3. **Step 1 - User details**:
   * User name: `resume-backend-s3-user`
   * Leave "Provide user access to the AWS Management Console" unchecked (this user is for programmatic API access only).
   * Click **Next**.
4. **Step 2 - Set permissions**:
   * Select **Attach policies directly**.
   * In the filter box, type `AmazonS3FullAccess`.
   * Check the box next to `AmazonS3FullAccess` and click **Next**.
5. **Step 3 - Review and create**:
   * Click **Create user**.
6. **Generate Credentials**:
   * Click on the user name `resume-backend-s3-user`.
   * Navigate to the **Security credentials** tab.
   * Scroll down to **Access keys** and click **Create access key**.
   * Select **Application running outside AWS** (or Other) and click **Next**.
   * Description: `Backend S3 access` -> Click **Create access key**.
7. **Copy and Save**:
   * **Access Key ID**: e.g., `AKIAIOSFODNN7EXAMPLE`
   * **Secret Access Key**: e.g., `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`
   *(Store these values securely—AWS will never show the Secret Access Key again).*

---

## Phase 3: Set Up Amazon RDS (MySQL Database)

Instead of running a local MySQL server, Amazon RDS manages backups, patches, and uptime.

1. Search for **RDS** in the top search bar and click on it.
2. Click the orange **Create database** button.
3. Configure the settings:
   * **Engine type**: **MySQL**
   * **Engine Version**: MySQL 8.0.x (default latest)
   * **Templates**: Choose **Free tier** *(CRITICAL: prevents unexpected charges)*.
   * **Settings**:
     * DB instance identifier: `resume-screening-db`
     * Master username: `admin`
     * Master password: Create a strong password (e.g. `ResumeCloud2026!`) and note it down.
   * **Instance configuration**: `db.t3.micro` or `db.t4g.micro` (included in Free Tier).
   * **Storage**:
     * Storage type: General Purpose SSD (gp2)
     * Allocated storage: 20 GiB
     * Storage autoscaling: Disable (uncheck) to maintain fixed capacity.
   * **Connectivity**:
     * Virtual private cloud (VPC): Default VPC
     * Public access: **Yes** *(Allows initial schema migration and EC2 connectivity)*.
     * VPC security group: Choose **Create new**, name it `rds-resume-sg`.
     * Availability Zone: No preference.
   * **Additional configuration** (Expand this dropdown):
     * **Initial database name**: `ai_resume_screening`
     * Enable automated backups: Optional (7 days is fine).
4. Click **Create database** at the bottom.
5. Wait 5–10 minutes until the database status changes from *Creating* to **Available**.
6. Click on `resume-screening-db` and copy the **Endpoint** under **Connectivity & security**:
   * Example: `resume-screening-db.czxxxxxx.ap-south-1.rds.amazonaws.com`

### Configure RDS Inbound Security Group Rule:
To allow your backend and migration script to reach MySQL on port 3306:
1. Under **Connectivity & security** of your database, click the link under **VPC security groups** (`rds-resume-sg`).
2. Select the security group checkbox, go to the **Inbound rules** tab, and click **Edit inbound rules**.
3. Add a rule:
   * **Type**: `MYSQL/Aurora` (Port 3306)
   * **Source**: `Anywhere-IPv4` (`0.0.0.0/0`)
4. Click **Save rules**.

---

## Phase 4: Import Database Schema into RDS

Run the repository's `database/schema.sql` against the RDS instance.

From your local computer terminal (PowerShell or Bash):

```bash
mysql -h <YOUR_RDS_ENDPOINT> -P 3306 -u admin -p ai_resume_screening < database/schema.sql
```
*(Enter your master password when prompted. The tables `users`, `jobs`, `resumes`, `candidates`, `screening_results` will be created on RDS).*

*Alternative if you don't have local `mysql` client installed:*
You can execute this step later directly inside the AWS EC2 instance!

---

## Phase 5: Code Integration (Enabling S3 Upload in Backend)

In the local repository, activate S3 uploads in `backend/app/routes/resume.py`.

Update the upload handler to save files to Amazon S3 when configured:

```python
# In backend/app/routes/resume.py
import os
from app.aws.s3_service import upload_resume_to_s3, generate_presigned_url
from app.utils.helpers import save_upload_file

@router.post("/upload")
def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOC and DOCX files are supported.")

    # 1. Save file locally for text extraction
    saved_path = save_upload_file(file)

    # 2. Upload to S3 if configured (supports IAM roles and explicit keys)
    s3_key = None
    s3_bucket = os.getenv("AWS_S3_BUCKET")
    if s3_bucket:
        try:
            with open(saved_path, "rb") as f:
                file_bytes = f.read()
            s3_res = upload_resume_to_s3(file_bytes, file.filename)
            s3_key = s3_res.get("key")
        except Exception as s3_err:
            print(f"Warning: S3 upload failed, falling back to local path: {s3_err}")

    # 3. Extract text & process NLP using local file
    parsed = parse_resume(saved_path)
    # Store s3_key if uploaded, else local saved_path...
```

Commit and push your changes to your Git repository:
```bash
git add .
git commit -m "Enable S3 upload support and AWS configurations"
git push origin main
```

---

## Phase 6: Launch and Deploy the Backend on AWS EC2

We will run the FastAPI backend on an Ubuntu EC2 virtual server.

### 1. Launch EC2 Instance:
1. In the AWS Console, search for **EC2** and click **Launch instance**.
2. **Name**: `resume-backend-server`
3. **Application and OS Images**: Select **Ubuntu** (Ubuntu Server 24.04 LTS).
4. **Instance type**: `t2.micro` (or `t3.micro` depending on region free tier).
5. **Key pair (login)**:
   * Click **Create new key pair**.
   * Key pair name: `resume-key`.
   * Key pair type: `RSA`, Private key format: `.pem`.
   * Click **Create key pair** (saves `resume-key.pem` to your computer).
6. **Network settings**:
   * Check **Allow SSH traffic from Anywhere**.
   * Check **Allow HTTP traffic from the internet**.
   * Click **Edit** (top right of Network settings).
   * Click **Add security group rule**:
     * **Type**: Custom TCP
     * **Port range**: `8000`
     * **Source type**: Anywhere (`0.0.0.0/0`)
     * **Description**: `FastAPI API server port`
7. Click **Launch instance**.

### 2. Connect to EC2 Terminal:
1. In the EC2 console, wait until your instance status is **Running**.
2. Select the instance and click the **Connect** button at the top.
3. Select **EC2 Instance Connect** and click **Connect**.
4. An Ubuntu command line terminal will open directly in your web browser.

### 3. Setup Python & Clone Repository on EC2:
Run the following commands in the browser terminal:

```bash
# 1. Update OS packages and install Python & Git
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git mysql-client

# 2. Clone your Git repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-Resume-Screening-System/backend

# 3. Create a Python Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 4. Install backend dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# 5. Create production .env file
nano .env
```

Paste your AWS configuration into `.env` (fill in your actual values):

```env
MYSQL_HOST=<YOUR_RDS_ENDPOINT>
MYSQL_PORT=3306
MYSQL_USER=admin
MYSQL_PASSWORD=<YOUR_RDS_MASTER_PASSWORD>
MYSQL_DATABASE=ai_resume_screening

AWS_ACCESS_KEY_ID=<YOUR_IAM_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<YOUR_IAM_SECRET_KEY>
AWS_REGION=ap-south-1
AWS_S3_BUCKET=<YOUR_S3_BUCKET_NAME>

JWT_SECRET=super-secret-production-jwt-key-2026
```
*(Press `Ctrl + O`, then `Enter` to save, then `Ctrl + X` to exit nano).*

### 4. Import Database Schema (if not done in Phase 4):
From the EC2 terminal:
```bash
mysql -h <YOUR_RDS_ENDPOINT> -u admin -p ai_resume_screening < ../database/schema.sql
```

### 5. Configure Background Service (Systemd):
To keep FastAPI running permanently in the background:

```bash
sudo nano /etc/systemd/system/resume-backend.service
```

Paste the following service definition:

```ini
[Unit]
Description=AI Resume Screening FastAPI Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/AI-Resume-Screening-System/backend
ExecStart=/home/ubuntu/AI-Resume-Screening-System/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
EnvironmentFile=/home/ubuntu/AI-Resume-Screening-System/backend/.env

[Install]
WantedBy=multi-user.target
```
*(Press `Ctrl + O`, `Enter`, then `Ctrl + X`).*

Now start and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start resume-backend
sudo systemctl enable resume-backend
```

Check that the server is active:
```bash
sudo systemctl status resume-backend
```

### 6. Verify Backend in your Browser:
Find your EC2 instance's **Public IPv4 address** from the EC2 console.
Visit:
`http://<YOUR_EC2_PUBLIC_IP>:8000/docs`

The Swagger API documentation will load live from your cloud server!

---

## Phase 7: Deploy the React Frontend on AWS Amplify

AWS Amplify provides automated CI/CD and CDN hosting for modern React / Vite applications.

### Step 1: Update API Base URL in Frontend
On your local computer, configure `frontend/.env`:

```env
# If using direct EC2 IP or domain:
VITE_API_BASE_URL=http://<YOUR_EC2_PUBLIC_IP>:8000

# OR if using AWS Amplify Reverse Proxy (see Step 3 below to avoid browser HTTPS/HTTP Mixed Content warnings):
# VITE_API_BASE_URL=
```

Commit and push this update to your GitHub repository:
```bash
git add frontend/.env
git commit -m "Configure production API URL for Amplify"
git push origin main
```

### Step 2: Deploy in AWS Amplify Console
1. Search for **AWS Amplify** in the AWS Console search bar and click on it.
2. Click **Host web app** (or **Deploy an app**).
3. Select **GitHub** and click **Next**.
4. Authorize AWS Amplify to access your GitHub repository.
5. Select your repository: `AI-Resume-Screening-System` and branch: `main`.
6. Configure Build Settings:
   * **App name**: `ai-resume-screening`
   * Amplify will automatically detect the included `amplify.yml` file in the root directory. If configuring manually, ensure build commands match:
     ```yaml
     version: 1
     frontend:
       phases:
         preBuild:
           commands:
             - cd frontend
             - npm ci --prefer-offline || npm install
         build:
           commands:
             - npm run build
       artifacts:
         baseDirectory: frontend/dist
         files:
           - '**/*'
       cache:
         paths:
           - frontend/node_modules/**/*
     ```
7. Click **Next** -> Click **Save and deploy**.
8. Wait 2–3 minutes while Amplify pulls your code, builds the bundle, and deploys it to AWS's global Content Delivery Network.
9. Click the generated live HTTPS URL:
   `https://main.d12345abcdef.amplifyapp.com`

### Step 3: Crucial Amplify Settings (SPA Routing & Mixed Content)

#### A. Single Page Application (SPA) 404 Fix:
To ensure browser refreshes on routes like `/dashboard`, `/jobs`, and `/candidates` don't return 404:
1. In the Amplify console, go to **App settings** -> **Rewrites and redirects**.
2. Click **Edit** and add a rule:
   * **Source address**: `</^[^.]+$|\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json)$)([^.]+$)/>`
   * **Target address**: `/index.html`
   * **Type**: `200 (Rewrite)`
3. Click **Save**.

#### B. Mixed Content Prevention (Connecting HTTPS Frontend to HTTP EC2):
Modern browsers block requests from an `https://` site (Amplify) to an `http://` endpoint (EC2 IP). Choose one of the following solutions:
* **Option 1 (Easiest - Amplify Reverse Proxy)**:
  In **Rewrites and redirects**, add a reverse proxy rule:
  * **Source address**: `/api/<*>`
  * **Target address**: `http://<YOUR_EC2_PUBLIC_IP>:8000/api/<*>`
  * **Type**: `200 (Rewrite)`
  Then in `frontend/.env` set `VITE_API_BASE_URL=` (empty string). Frontend requests will be securely routed through Amplify's HTTPS domain without any browser mixed-content blocks!
* **Option 2 (Amazon API Gateway)**:
  Create an HTTP API in API Gateway (as detailed in `/backend/app/aws/api_gateway_config.md`) that proxies to your EC2 instance. Set `VITE_API_BASE_URL=https://<api-id>.execute-api.ap-south-1.amazonaws.com`.

---

## Phase 8: End-to-End System Testing Checklist

Verify your entire cloud application in action:

1. **Access Frontend**: Open the live Amplify URL in your browser.
2. **Register**: Create a new recruiter account (`/register`). Check your RDS MySQL `users` table to verify row insertion.
3. **Login**: Login with your recruiter credentials (`/login`). Verify that JWT authentication functions properly.
4. **Create Job**: Post a new job (e.g. *Full Stack Python Developer*, required skills: `python, react, sql, aws, git`).
5. **Upload Resume**: Upload a sample candidate resume (`.pdf` or `.docx`).
   * Check your **Amazon S3 Bucket**: You will see the new resume file stored under the `resumes/` folder!
6. **Screen Candidate**: Click **Analyze** on the candidate.
   * The EC2 backend extracts text, scores candidate skills against the job, and calculates weighted match percentages.
7. **Candidate Ranking**: View candidate ranking per job with visual score bars.

---

## Phase 9: Cost Management & Free Tier Safety

To ensure your AWS account remains free or incurs minimal cost:

1. **Set Up a Billing Alarm**:
   * Search for **CloudWatch** -> Click **Alarms** -> **Create alarm**.
   * Metric: `EstimatedCharges` -> Threshold: `$5.00` -> Add your email address for alerts.
2. **Instance Sizing**: Keep your EC2 instance on `t2.micro` / `t3.micro` and RDS on `db.t3.micro` / `db.t4g.micro`.
3. **To Pause/Stop the Project**:
   * If you're not actively using the project:
     * In the EC2 console: Select instance -> **Instance state** -> **Stop instance** (incurs $0 compute charges while stopped).
     * In the RDS console: Select database -> **Actions** -> **Stop temporarily**.
