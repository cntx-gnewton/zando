-- User Management Functions for Zando Genomic Analysis
-- Part of Migration 0004

-- Function to register a new user
CREATE OR REPLACE FUNCTION register_user(
    p_email TEXT,
    p_password TEXT,
    p_first_name TEXT DEFAULT NULL,
    p_last_name TEXT DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    new_user_id INTEGER;
BEGIN
    -- Check if user already exists
    IF EXISTS (SELECT 1 FROM app_user WHERE email = p_email) THEN
        RAISE EXCEPTION 'User with email % already exists', p_email;
    END IF;
    
    -- Insert new user
    INSERT INTO app_user (
        email,
        password_hash,
        first_name,
        last_name,
        created_at,
        is_active,
        is_admin
    ) VALUES (
        p_email,
        hash_password(p_password),
        p_first_name,
        p_last_name,
        NOW(),
        TRUE,
        FALSE
    ) RETURNING user_id INTO new_user_id;
    
    -- Create default preferences
    INSERT INTO user_preference (
        user_id,
        email_notifications,
        dark_mode,
        language,
        created_at,
        updated_at
    ) VALUES (
        new_user_id,
        TRUE,
        FALSE,
        'en',
        NOW(),
        NOW()
    );
    
    RETURN new_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to authenticate user
CREATE OR REPLACE FUNCTION authenticate_user(
    p_email TEXT,
    p_password TEXT
) RETURNS TABLE (
    user_id INTEGER,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    is_admin BOOLEAN,
    last_login TIMESTAMP
) AS $$
BEGIN
    -- Check credentials and return user info
    RETURN QUERY
    SELECT 
        u.user_id,
        u.email,
        u.first_name,
        u.last_name,
        u.is_admin,
        u.last_login
    FROM app_user u
    WHERE u.email = p_email
    AND u.is_active = TRUE
    AND verify_password(p_password, u.password_hash);
    
    -- Update last login time if user found
    UPDATE app_user
    SET last_login = NOW()
    WHERE email = p_email
    AND verify_password(p_password, password_hash);
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Function to log user actions
CREATE OR REPLACE FUNCTION log_user_action(
    p_user_id INTEGER,
    p_action_type TEXT,
    p_entity_type TEXT,
    p_entity_id INTEGER,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_details JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_log (
        user_id,
        action_type,
        entity_type,
        entity_id,
        action_timestamp,
        ip_address,
        user_agent,
        action_details
    ) VALUES (
        p_user_id,
        p_action_type,
        p_entity_type,
        p_entity_id,
        NOW(),
        p_ip_address,
        p_user_agent,
        p_details
    );
END;
$$ LANGUAGE plpgsql;