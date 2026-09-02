# turbo-gateway

Gateway service for routing and forwarding webhook traffic via AWS Lambda.

## Structure

```
forwarder/    - Lambda that verifies and forwards incoming webhook requests
.github/
  workflows/
    deploy.yml              - CI pipeline: build and push Docker images to ECR
```

## Lambda functions

The forwarder Lambda is packaged as a Docker image (Python 3.12) and deployed to AWS ECR.

### forwarder

Validates incoming webhook payloads using HMAC-SHA256 signature verification, then forwards them to SQS. The shared secret is fetched from AWS Secrets Manager via the `WEBHOOK_SECRET_NAME` environment variable.

## CI/CD

The `deploy` workflow triggers on:

- **Push to `main`** — builds and pushes the forwarder image if its files changed
- **GitHub Release** — builds and pushes the forwarder image

Images are pushed to ECR with two tags: the commit SHA and `latest`.

Lambda function code updates are managed separately via Terraform.

### AWS credentials

| Environment | Auth method |
|---|---|
| Dev | `cg-datasci-dev-ci` user credentials used directly |
| Prod | `cg-datasci-prod-clv-ci` user credentials used directly |

### Required GitHub secrets

| Secret | Used for |
|---|---|
| `AWS_ACCESS_KEY_ID` | Dev ECR push |
| `AWS_SECRET_ACCESS_KEY` | Dev ECR push |
| `AWS_PROD_ACCESS_KEY_ID` | Prod ECR push |
| `AWS_PROD_SECRET_ACCESS_KEY` | Prod ECR push |

## Local development

Requires [uv](https://github.com/astral-sh/uv).

```bash
cd forwarder
uv sync
```
