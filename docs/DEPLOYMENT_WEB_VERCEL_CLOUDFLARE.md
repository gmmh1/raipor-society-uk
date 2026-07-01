# Web Deployment: Vercel + Cloudflare + GitHub

## Objective

Deploy the website frontend from GitHub to Vercel, with domain and edge protection managed in Cloudflare.

## 1) GitHub repository setup

1. Push repository to GitHub.
2. Protect `main` branch with required checks:
   - backend job
   - mobile job
   - web job
3. Require pull request review and linear history.

## 2) Vercel project setup

1. Create Vercel project from GitHub repository.
2. Set root directory to `web`.
3. Configure environment variables:
   - `NEXT_PUBLIC_API_BASE_URL`
   - `NEXT_PUBLIC_ENVIRONMENT`
4. Enable preview deployments for pull requests.
5. Promote `main` deployment to production.

## 3) Cloudflare domain setup

1. Add domain zone to Cloudflare.
2. In DNS, create:
   - `A` or `CNAME` for root domain to Vercel target
   - `CNAME` for `www` to Vercel target
3. Enable proxy (orange cloud) for public records.
4. Enable automatic HTTPS and minimum TLS 1.2.

## 4) Cloudflare security baseline

1. Turn on WAF managed rules.
2. Add rate limiting for:
   - `/api/auth/*`
   - `/api/contact/*`
   - `/api/vote/*`
3. Add bot mitigation for form endpoints.
4. Optional: Turnstile on public forms.

## 5) API routing model

- Frontend hosted on Vercel.
- Backend hosted separately (self-hosted or container host).
- Frontend consumes backend via `NEXT_PUBLIC_API_BASE_URL`.
- CORS allowed only from trusted frontend domains.

## 6) Operational checks

1. Verify preview URL on each PR.
2. Verify production URL after merge.
3. Confirm DNS propagation and TLS health.
4. Confirm Cloudflare caching behavior.
5. Confirm login, payments, and voting smoke tests.

## 7) Rollback strategy

- Vercel: promote previous successful deployment.
- Backend: rollback to previous container image or release tag.
- Cloudflare: keep a DNS export and rules backup.
