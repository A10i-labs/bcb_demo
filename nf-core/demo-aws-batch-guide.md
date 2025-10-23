# Running nf-core/demo on AWS Batch

**Pipeline:** nf-core/demo v1.0.2  
**Date:** October 2025

---
---

## Architecture

```
EC2 Instance (Nextflow head node)
    ├── IAM Role: YOUR-EC2-INSTANCE-ROLE
    ├── Permissions: S3 + Batch
    └── Submits jobs to AWS Batch
           ↓
AWS Batch Job Queue (YOUR-JOB-QUEUE)
    └── Connected to Compute Environment
           ↓
Compute Environment (YOUR-COMPUTE-ENV)
    ├── Type: EC2 (NOT Fargate)
    ├── Instance Role: YOUR-BATCH-INSTANCE-ROLE
    └── Launches EC2 instances dynamically
           ↓
Docker Containers (FastQC, seqtk, etc.)
    ├── Fusion: Direct S3 access without staging
    └── Wave: Container provisioning via Seqera
```

---

## Step-by-Step Setup

### Step 1: Create Seqera Platform Token

**Why needed:** Wave (required by Fusion) needs authentication with Seqera Platform.

1. **Sign up for Seqera Platform** (free):

   - Go to https://cloud.seqera.io
   - Create a free account (takes 1-2 minutes)

2. **Generate access token**:

   - Log in to Seqera Platform
   - Click your username (top right) → **Your tokens**
   - Click **Add token** or **New token**
   - Name it: `nextflow-batch`
   - Copy the generated token

3. **Set environment variable on EC2**:

   ```bash
   export TOWER_ACCESS_TOKEN="your-token-here"
   ```

4. **Make it permanent**:

   ```bash
   echo 'export TOWER_ACCESS_TOKEN="your-token-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

5. **Verify**:
   ```bash
   echo $TOWER_ACCESS_TOKEN
   ```

---

### Step 2: Configure IAM Roles

You need **two different IAM roles** for AWS Batch to work properly:

#### Role 1: EC2 Instance Role (for Nextflow head node)

**Purpose:** Allows your EC2 instance to submit jobs to AWS Batch and access S3.

**Example Role :** `Ram-batch-role`

**Steps:**

1. Go to **IAM** → **Roles** → Find your EC2 instance role
2. Click **Add permissions** → **Attach policies**
3. Attach these managed policies:
   - `AmazonS3FullAccess` (or custom policy below)
   - `AWSBatchFullAccess`

**You can add Custom S3 Policy (more secure than full access):**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:ListBucket", "s3:GetBucketLocation"],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

---

#### Role 2: Batch Compute Environment Instance Role

**Purpose:** Allows EC2 instances launched by AWS Batch to pull Docker images and access S3.

**Example Role Name:** `YOUR-BATCH-INSTANCE-ROLE` or `ecsInstanceRole`

**Steps to create:**

1. Go to **IAM** → **Roles** → **Create role**
2. Select **AWS service**
3. Select **Elastic Container Service**
4. Choose **EC2 Role for Elastic Container Service**
5. Click **Next**
6. Attach policies:
   - `AmazonEC2ContainerServiceforEC2Role` (automatically attached)
   - Add the custom S3 policy above (if needed)
7. Name it: `YOUR-BATCH-INSTANCE-ROLE`
8. Create the role

> **Note:** The trust relationship is **automatically created** when you follow steps 2-4 above. It allows EC2 and ECS services to assume this role. You don't need to manually configure it.

---

### Step 3: Create AWS Batch Compute Environment

**Important:** Must be EC2-based, NOT Fargate!

1. Go to **AWS Batch** → **Compute environments** → **Create**

2. **Configuration:**

   - **Name:** `YOUR-COMPUTE-ENV` (example: `nf-demo-ec2-ce`)
   - **Type:** Managed
   - **Orchestration type:** ⚠️ **EC2** (NOT Fargate)

3. **Service role:**

   - Use `AWSServiceRoleForBatch` (auto-created)

4. **Instance role:**

   - Select: `YOUR-BATCH-INSTANCE-ROLE` (created in Step 2)

5. **Instance configuration:**

   - **Minimum vCPUs:** `0` (save costs when idle)
   - **Desired vCPUs:** `0` (start at zero)
   - **Maximum vCPUs:**
     - `8` for demo/testing
     - `96-256+` for production pipelines

6. **Networking:**

   - Select your VPC
   - Select subnets (use multiple for high availability)
   - Security group: Allow outbound traffic

7. **Additional settings:**

   - Enable Spot instances (optional, for cost savings)
   - Allocation strategy: `BEST_FIT_PROGRESSIVE`

8. Click **Create compute environment**

---

### Step 4: Create AWS Batch Job Queue

1. Go to **AWS Batch** → **Job queues** → **Create**

2. **Configuration:**

   - **Name:** `YOUR-JOB-QUEUE` (example: `nf-demo-queue`)
   - **Priority:** `1`
   - **State:** Enabled

3. **Compute environments:**

   - Click **Add compute environment**
   - Select: `YOUR-COMPUTE-ENV` (created in Step 3)
   - Set order: `1`

4. Click **Create job queue**

---

### Step 5: Create Nextflow Configuration

Create a file named `nextflow.config` in the directory where you'll run Nextflow:

```groovy
// Enable Fusion for efficient S3 access
fusion {
  enabled = true
}

// Enable Wave for container provisioning
wave {
  enabled = true
}

// AWS Configuration
aws {
  region = 'YOUR-AWS-REGION'  // Example: 'us-east-2'
  batch {
    cliPath = '/usr/local/bin/aws'
  }
}

// Configure AWS Batch executor
process {
  executor = 'awsbatch'
  queue = 'YOUR-JOB-QUEUE'  // Example: 'nf-demo-queue'
}
```

**Key Points:**

- **Fusion** enables direct S3 file access without staging files to local disk
- **Wave** is required by Fusion and handles container provisioning
- This config is automatically loaded when in the same directory as your command

---

## Running the Pipeline

### First, Install Java and Nextflow

```bash
# Verify your OS (should show Amazon Linux 2)
cat /etc/os-release

# Update system (Amazon Linux)
sudo yum update -y

# Install Java (required for Nextflow)
sudo yum install -y java-21-amazon-corretto-devel

# Verify Java ≥ 11 is installed
java -version

# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
nextflow -version
```

---

### Option 1: With Built-in Test Data (Recommended)

The easiest way to test your setup:

```bash
nextflow run nf-core/demo \
  -r 1.0.2 \
  -profile test \
  -bucket-dir s3://YOUR-BUCKET/work \
  --outdir s3://YOUR-BUCKET/results
```

**Benefits:**

- Uses small built-in test datasets
- No need to create samplesheet.csv
- Runs in 1-2 minutes
- Perfect for validating your setup

---

### Option 2: With Custom Samplesheet

For your own data:

```bash
nextflow run nf-core/demo \
  -r 1.0.2 \
  -profile awsbatch \
  -bucket-dir s3://YOUR-BUCKET/work \
  --outdir s3://YOUR-BUCKET/results \
  --input ./samplesheet.csv
```

**Sample samplesheet.csv:**

```csv
sample,fastq_1,fastq_2
SAMPLE1,s3://YOUR-BUCKET/sample1_R1.fastq.gz,s3://YOUR-BUCKET/sample1_R2.fastq.gz
SAMPLE2,s3://YOUR-BUCKET/sample2_R1.fastq.gz,s3://YOUR-BUCKET/sample2_R2.fastq.gz
```

---

## Verification Checklist

Before running your pipeline, verify all of these:

### Environment Setup

- [ ] `TOWER_ACCESS_TOKEN` is set (`echo $TOWER_ACCESS_TOKEN`)
- [ ] `nextflow.config` exists in current directory
- [ ] `nextflow.config` has Fusion + Wave enabled
- [ ] Nextflow is installed (`nextflow -version`)

### IAM Permissions

- [ ] EC2 instance role has `AmazonS3FullAccess`
- [ ] EC2 instance role has `AWSBatchFullAccess`
- [ ] Batch instance role exists (`YOUR-BATCH-INSTANCE-ROLE`)
- [ ] Batch instance role has `AmazonEC2ContainerServiceforEC2Role`

### AWS Batch Configuration

- [ ] Compute environment is **EC2-based** (not Fargate)
- [ ] Compute environment state is **ENABLED**
- [ ] Compute environment instance role is set correctly
- [ ] Job queue is created and **ENABLED**
- [ ] Job queue is connected to EC2 compute environment

### AWS Resources

- [ ] S3 bucket exists
- [ ] S3 bucket is in same region as Batch queue
- [ ] Region in `nextflow.config` matches your resources
- [ ] VPC and subnets are configured correctly

---
