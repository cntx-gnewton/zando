-- Utility Functions for Zando Genomic Analysis
-- Part of Migration 0004

-- Function to update timestamps automatically via triggers
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random UUID with prefix
CREATE OR REPLACE FUNCTION generate_prefixed_uuid(prefix TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN prefix || '_' || REPLACE(uuid_generate_v4()::TEXT, '-', '');
END;
$$ LANGUAGE plpgsql;

-- Function to hash a password securely using pgcrypto
CREATE OR REPLACE FUNCTION hash_password(password TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN crypt(password, gen_salt('bf', 10));
END;
$$ LANGUAGE plpgsql;

-- Function to verify a password against stored hash
CREATE OR REPLACE FUNCTION verify_password(password TEXT, stored_hash TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN stored_hash = crypt(password, stored_hash);
END;
$$ LANGUAGE plpgsql;