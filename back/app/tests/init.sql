--
-- PostgreSQL database dump
--

-- Dumped from database version 14.4
-- Dumped by pg_dump version 14.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: decrease_item_count(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.decrease_item_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
    UPDATE item
    SET count = count - 1
    WHERE id = NEW.item_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.decrease_item_count() OWNER TO postgres;

--
-- Name: increase_item_count(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.increase_item_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$

BEGIN
    UPDATE item
    SET count = count + 1
    WHERE id = OLD.item_id;
    RETURN OLD;
END;
$$;


ALTER FUNCTION public.increase_item_count() OWNER TO postgres;

--
-- Name: update_order_total(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_order_total() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE "order"
    SET total = (
        SELECT SUM(item.price)
        FROM order_items
        INNER JOIN item ON order_items.item_id = item.id
        WHERE order_items.order_id = NEW.order_id
    )
    WHERE "order".id = NEW.order_id;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_order_total() OWNER TO postgres;

--
-- Name: update_order_total_after_delete(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_order_total_after_delete() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE public."order" o
    SET total = (
        SELECT COALESCE(SUM(i.price), 0)
        FROM order_items oi
        INNER JOIN item i ON oi.item_id = i.id
        WHERE oi.order_id = o.id
    )
    WHERE o.id = NEW.order_id OR o.id = OLD.order_id;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_order_total_after_delete() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: conversation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.conversation (
    order_id integer NOT NULL,
    "time" timestamp without time zone DEFAULT date_trunc('second'::text, (now())::timestamp without time zone) NOT NULL,
    owner character varying(10) NOT NULL,
    replica character varying(512) NOT NULL
);


ALTER TABLE public.conversation OWNER TO postgres;

--
-- Name: item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.item (
    id integer NOT NULL,
    name character varying(70) NOT NULL,
    count integer DEFAULT 100 NOT NULL,
    is_primary boolean NOT NULL,
    price numeric(6,2) NOT NULL
);


ALTER TABLE public.item OWNER TO postgres;

--
-- Name: item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.item ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: order; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    total numeric(6,2) DEFAULT 0 NOT NULL,
    "time" timestamp without time zone DEFAULT date_trunc('second'::text, (now())::timestamp without time zone) NOT NULL,
    was_suggested boolean DEFAULT false NOT NULL,
    is_closed boolean DEFAULT false NOT NULL
);


ALTER TABLE public."order" OWNER TO postgres;

--
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public."order" ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    order_id integer NOT NULL,
    item_id integer NOT NULL,
    id integer NOT NULL,
    is_upselled boolean DEFAULT false NOT NULL
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.order_items ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.order_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: item item_name_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_name_unique UNIQUE (name);


--
-- Name: item item_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.item
    ADD CONSTRAINT item_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: order_items item_added_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER item_added_trigger BEFORE INSERT ON public.order_items FOR EACH ROW EXECUTE FUNCTION public.decrease_item_count();


--
-- Name: order_items item_deleted_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER item_deleted_trigger AFTER DELETE ON public.order_items FOR EACH ROW EXECUTE FUNCTION public.increase_item_count();


--
-- Name: order_items order_total_after_delete; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER order_total_after_delete AFTER DELETE ON public.order_items FOR EACH ROW EXECUTE FUNCTION public.update_order_total_after_delete();


--
-- Name: order_items order_total_after_insert_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER order_total_after_insert_trigger AFTER INSERT ON public.order_items FOR EACH ROW EXECUTE FUNCTION public.update_order_total_after_delete();


--
-- Name: order_items item_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT item_id FOREIGN KEY (item_id) REFERENCES public.item(id);


--
-- PostgreSQL database dump complete
--