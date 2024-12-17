"""Supabase configuration."""

SUPABASE_URL = "https://jvfjxlpplbyrafasobzl.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2Zmp4bHBwbGJ5cmFmYXNvYnpsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM4OTg2NzUsImV4cCI6MjA0OTQ3NDY3NX0.1_tTwBDg1ibnlBbe6PyzID8CucrkQlXEUsA5dyNQ_g0"
SUPABASE_SERVICE_ROLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2Zmp4bHBwbGJ5cmFmYXNvYnpsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzg5ODY3NSwiZXhwIjoyMDQ5NDc0Njc1fQ.sk2X5le3Rt3O0krvJREk0Cn4H8bI3V2rwx5Md2jg_SI"
DB_PASSWORD = "fogdif-7voHxi-ryfqug"

# Database connection string
DATABASE_URL = "postgresql://postgres.jvfjxlpplbyrafasobzl:fogdif-7voHxi-ryfqug@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

class SupabaseConfig:
    def __init__(self):
        """Инициализация конфигурации Supabase."""
        self.url = "https://jvfjxlpplbyrafasobzl.supabase.co"
        self.key = SUPABASE_SERVICE_ROLE
