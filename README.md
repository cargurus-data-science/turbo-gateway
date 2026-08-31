# turbo-gateway

Gateway service for routing and authorizing webhook traffic via AWS Lambda.

## Structure

```
authorizer/   - Lambda that verifies incoming webhook signatures (HMAC-SHA256)
forwarder/    - Lambda that forwards verified requests downstream
.github/
  workflows/
    deploy.yml              - CI pipeline: build and push Docker images to ECR
```

## Lambda functions

Both Lambdas are packaged as Docker images (Python 3.12) and deployed to AWS ECR.

### authorizer

Validates webhook payloads using HMAC-SHA256 signature verification. The shared secret is fetched from AWS Secrets Manager via the `WEBHOOK_SECRET_NAME` environment variable.

### forwarder

Forwards verified webhook payloads to the configured downstream target.

## CI/CD

The `deploy` workflow triggers on:

- **Push to `main`** — builds and pushes only the Lambda(s) whose files changed
- **GitHub Release** — builds and pushes both Lambdas

Images are pushed to ECR with two tags: the commit SHA and `latest`.

Lambda function code updates are managed separately via Terraform.

### AWS credentials

| Environment | Auth method |
|---|---|
| Dev | `cg-datasci-dev-ci` user assumes `cg-datasci-dev-ci-role` |
| Prod | `cg-datasci-prod-clv-ci` user credentials used directly |

### Required GitHub secrets

| Secret | Used for |
|---|---|
| `AWS_ACCESS_KEY_ID` | Dev ECR push |
| `AWS_SECRET_ACCESS_KEY` | Dev ECR push |
| `AWS_ACCOUNT_ID` | Dev IAM role ARN |
| `AWS_PROD_ACCESS_KEY_ID` | Prod ECR push |
| `AWS_PROD_SECRET_ACCESS_KEY` | Prod ECR push |

## Local development

Requires [uv](https://github.com/astral-sh/uv).

```bash
cd authorizer
uv sync
```
