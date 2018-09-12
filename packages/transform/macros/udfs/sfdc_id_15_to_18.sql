{% macro sfdc_id_15_to_18() %}
CREATE OR REPLACE FUNCTION {{target.schema}}.id15to18(inputid text)
  RETURNS text
IMMUTABLE
LANGUAGE plpgsql
AS $$
DECLARE flags INTEGER DEFAULT 0;
DECLARE suffix TEXT DEFAULT '';
DECLARE chr TEXT DEFAULT NULL;
BEGIN
    IF char_length(inputid) != 15 THEN
        RETURN inputid;
    END IF;
    FOR i IN 0 .. 2 LOOP
        flags := 0;
        FOR j IN 0 .. 4 LOOP
            chr := substring(inputid FROM (i)*5+j+1 FOR 1);
            IF ( ascii(chr) >= ascii('A') AND ascii(chr) <= ascii('Z') ) THEN
                flags := flags + (1 << j);
            END IF;
        END LOOP;
        suffix := suffix || substring('ABCDEFGHIJKLMNOPQRSTUVWXYZ012345' FROM flags+1 FOR 1);
    END LOOP;
    RETURN inputid || suffix;
END;
$$;
{% endmacro %}