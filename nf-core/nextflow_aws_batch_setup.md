
# 🚀 Nextflow on AWS Batch — Steps 1–4 Setup Guide

This guide explains how to set up **AWS Batch** and configure **Nextflow** to run with the `awsbatch` executor.  
It includes steps from creating a Compute Environment to configuring Nextflow.

---

## 🧩 Step 1 — Create an AWS Batch Compute Environment (EC2)

1. Go to **AWS Console → AWS Batch → Environments → Create compute environment**  
2. **Compute platform:** Amazon EC2  
3. **Orchestration type:** Managed  
4. **Name:** `nextflow-batch-ami-env`  
5. **Service role:** AWSServiceRoleForBatch (default)  
6. **Instance role:** `ec2-role` (create it if not exists — see below)  
7. **Provisioning model:** On-Demand  
8. **Maximum vCPUs:** e.g. 32  
9. **Instance types:** m5.large, m5.xlarge (adjust as needed)  
10. **Custom AMI:** Paste your custom AMI ID that includes the AWS CLI installation.  
11. **Networking:**  
    - VPC: choose your VPC  
    - Subnets: public subnets  
    - Assign public IP: enabled  
12. **Create compute environment**  
13. Wait until **State: Enabled** and **Status: Valid**.

### ✅ Creating the `ec2-role` (if you don’t have it)
Go to **IAM → Roles → Create role**:  
- Trusted entity: **AWS service** → choose **EC2**  
- Attach permissions:  
  - `AmazonEC2ContainerServiceforEC2Role`  
  - `AmazonS3FullAccess`  
  - *(Optional)* `AmazonSSMManagedInstanceCore` (for Session Manager access)  
- Name it **`ec2-role`**  

Now return to the Compute Environment and select this role under **Instance role**.

---

## 🧩 Step 2 — Create a Job Queue

1. Go to **AWS Batch → Job queues → Create**  
2. Name: `nextflow-job-queue`  
3. Priority: 1  
4. State: Enabled  
5. Add your Compute Environment (`nextflow-batch-ami-env`) to the queue  
6. Save and confirm the Job Queue shows **Status: Valid**.

---

## 🧩 Step 3 — Create a Job Definition

1. Go to **AWS Batch → Job definitions → Create**  
2. Name: `nextflow-job-def`  
3. Platform: EC2  
4. Image: `quay.io/nextflow/bash`  
5. Command: `["echo", "hello world"]`  
6. Leave execution role empty (Batch uses the compute environment’s role)  
7. Save — your job definition will appear as **Active**.

---

## 🧩 Step 4 — Configure Nextflow to Use AWS Batch

Create or edit `nextflow.config` in your home directory (`/home/ramin/nextflow.config`).

```groovy
plugins {
  id 'nf-amazon'
}

process {
  executor  = 'awsbatch'
  queue     = 'nextflow-job-queue'
  container = 'quay.io/nextflow/bash'
  cpus      = 1
  memory    = '1 GB'
  time      = '1h'
}

aws {
  region = 'us-east-2'
  batch {
    jobQueue      = 'nextflow-job-queue'
    jobDefinition = 'nextflow-job-def'
    // Path to AWS CLI on your custom AMI
    cliPath       = '/usr/local/bin/aws'
  }
}

workDir = 's3://a10i-bcb-demo/nextflow-work/'
```

Then, run your first test pipeline:
```bash
nextflow run nextflow-io/hello -profile awsbatch -c /home/ramin/nextflow.config
```

✅ If everything is set up correctly, AWS Batch will launch jobs from your custom AMI and Nextflow will execute successfully.

---

**Summary:**  
After Step 4, you have:
- A **Batch Compute Environment** using your custom AMI  
- A **Job Queue** and **Job Definition** ready for Nextflow  
- A working `nextflow.config` file for `awsbatch` execution
