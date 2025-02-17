-- Create a function to atomically decrement credits
CREATE OR REPLACE FUNCTION public.decrement_credits(user_id UUID)
RETURNS TABLE (remaining_credits INTEGER) 
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH updated AS (
        UPDATE usage
        SET credits = credits - 1
        WHERE profile_id = user_id
        AND credits > 0
        RETURNING credits
    )
    SELECT credits FROM updated;
END;
$$; 