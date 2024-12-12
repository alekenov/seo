#!/bin/bash
PGPASSWORD=fogdif-7voHxi-ryfqug psql -h aws-0-eu-central-1.pooler.supabase.com -p 6543 -d postgres -U postgres.jvfjxlpplbyrafasobzl -f scripts/analyze_pages.sql
