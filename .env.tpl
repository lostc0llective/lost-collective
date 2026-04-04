KLAVIYO_PRIVATE_KEY=op://Private/6agun5mm4yflcfg5yovqoufvnu/password
KLAVIYO_PUBLIC_KEY=op://Private/6agun5mm4yflcfg5yovqoufvnu/Public Key

SHOPIFY_ADMIN_TOKEN=op://Private/6u6evrxttlqexvzu6et4bpcl3y/Admin Token
SHOPIFY_THEME_ID_PRODUCTION=op://Private/6u6evrxttlqexvzu6et4bpcl3y/Live Theme ID
SHOPIFY_THEME_ID_STAGING=op://Private/6u6evrxttlqexvzu6et4bpcl3y/Theme ID Staging
SHOPIFY_THEME_ID_BACKUP=op://Private/6u6evrxttlqexvzu6et4bpcl3y/Theme ID Backup
# SHOPIFY_ENV defaults to staging — set to "production" only when intentionally targeting live
SHOPIFY_ENV=staging

# Webhooks — set WEBHOOK_ENDPOINT to your live handler URL when deploying
# For local testing: python3 scripts/webhook_receiver.py  (listens on localhost:8765)
WEBHOOK_ENDPOINT=https://lost-collective-webhooks.fragrant-union-3149.workers.dev/webhook
SHOPIFY_WEBHOOK_SECRET=

CLOUDFLARE_ACCOUNT_ID=op://Private/3asxpxb74yqfcrqzd7tddrspby/Account ID
CLOUDFLARE_API_TOKEN=op://Private/3asxpxb74yqfcrqzd7tddrspby/API Token
