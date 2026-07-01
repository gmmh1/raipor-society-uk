# Cloudflare DNS Records (Example)

Replace placeholders with your real values.

- Type: CNAME
  Name: www
  Target: cname.vercel-dns.com
  Proxy: Proxied

- Type: A
  Name: @
  Target: 76.76.21.21
  Proxy: Proxied

- Type: CNAME
  Name: api
  Target: api.your-backend-domain.example
  Proxy: Proxied
