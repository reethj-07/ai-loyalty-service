-- Enable pgvector extension (available free on all Supabase plans)
CREATE EXTENSION IF NOT EXISTS vector;

-- Store campaign embeddings
ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Store member behavior embeddings
CREATE TABLE IF NOT EXISTS member_behavior_embeddings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id uuid REFERENCES members(id),
    summary_text text,
    embedding vector(384),
    created_at timestamptz DEFAULT now()
);

-- IVFFlat index for fast ANN search
CREATE INDEX IF NOT EXISTS campaigns_embedding_ivfflat_idx
    ON campaigns USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

CREATE INDEX IF NOT EXISTS member_behavior_embeddings_ivfflat_idx
    ON member_behavior_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50);

-- RPC helper for Supabase: semantic campaign match by embedding
CREATE OR REPLACE FUNCTION match_campaigns_by_embedding(
    query_embedding vector(384),
    match_count int DEFAULT 3
)
RETURNS TABLE (
    id uuid,
    name text,
    campaign_type text,
    objective text,
    estimated_roi numeric,
    similarity float
)
LANGUAGE sql
AS $$
    SELECT
        c.id,
        c.name,
        c.campaign_type,
        c.objective,
        c.estimated_roi,
        1 - (c.embedding <=> query_embedding) AS similarity
    FROM campaigns c
    WHERE c.embedding IS NOT NULL
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
$$;
