# Web Frontend (Next.js)

This folder contains the website platform for:

- Public website pages
- Member portal pages
- Admin portal pages

## Routes scaffolded

- Public: `/`, `/about`, `/programs`, `/events`, `/donate`, `/contact`
- Member: `/member/dashboard`, `/member/events`, `/member/documents`, `/member/voting`
- Admin: `/admin/dashboard`, `/admin/membership`, `/admin/finance`, `/admin/governance`

## Local development

```bash
cd web
npm install
npm run dev
```

## Environment

Copy `.env.example` and set:

- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_ENVIRONMENT`
