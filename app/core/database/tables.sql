-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'automation', 'viewer')),
    created_at TIMESTAMP DEFAULT now()
);

-- encoders table
CREATE TABLE encoders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    port INTEGER DEFAULT 80,
    status VARCHAR(50) DEFAULT 'offline',
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ip_address)
);

-- stream_keys table
CREATE TABLE stream_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encoder_id UUID REFERENCES encoders(id),
    name VARCHAR(255) NOT NULL,
    input_stream_key TEXT NOT NULL,  -- AJA to Watchtower
    output_stream_key TEXT NOT NULL, -- Watchtower to YouTube
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- logs table
CREATE TABLE logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encoder_id UUID REFERENCES encoders(id) ON DELETE CASCADE,
    level TEXT CHECK (level IN ('INFO', 'WARN', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    raw_json JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encoder_id UUID REFERENCES encoders(id) ON DELETE CASCADE,
    alert_type TEXT CHECK (alert_type IN ('Stream Down', 'Stream Up', 'Stream Quality Alert')),
    created_at TIMESTAMP DEFAULT now()
);

-- Store stream configurations
CREATE TABLE stream_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encoder_id UUID REFERENCES encoders(id),
    bitrate INTEGER,
    resolution VARCHAR(20),
    frame_rate INTEGER,
    audio_channels INTEGER,
    audio_bitrate INTEGER,
    protocol VARCHAR(10),
    encoding VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Store encoder logs
CREATE TABLE encoder_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    encoder_id UUID REFERENCES encoders(id),
    level VARCHAR(20) NOT NULL,
    message TEXT,
    raw_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Store transcription status
CREATE TABLE transcription_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stream_key_id UUID REFERENCES stream_keys(id),
    is_active BOOLEAN DEFAULT false,
    last_error TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
