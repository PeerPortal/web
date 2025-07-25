-- SQL script to create tables for enhanced matching algorithm

-- University rankings table for tier-based matching
CREATE TABLE IF NOT EXISTS university_rankings (
    id SERIAL PRIMARY KEY,
    university VARCHAR(255) NOT NULL,
    ranking INTEGER,
    country VARCHAR(100),
    region VARCHAR(100),
    tier VARCHAR(20), -- 'top_10', 'top_50', 'top_100', etc.
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(university)
);

-- Major relations table for related major matching
CREATE TABLE IF NOT EXISTS major_relations (
    id SERIAL PRIMARY KEY,
    major1 VARCHAR(255) NOT NULL,
    major2 VARCHAR(255) NOT NULL,
    relation_type VARCHAR(50), -- 'related', 'subcategory', 'interdisciplinary'
    similarity_score DECIMAL(3,2), -- 0.0 to 1.0
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(major1, major2)
);

-- Major categories table for broad field matching
CREATE TABLE IF NOT EXISTS major_categories (
    id SERIAL PRIMARY KEY,
    major VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- 'STEM', 'Business', 'Liberal Arts', etc.
    subcategory VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(major, category)
);

-- Insert sample university rankings
INSERT INTO university_rankings (university, ranking, country, tier) VALUES
('Stanford University', 2, 'USA', 'top_10'),
('MIT', 1, 'USA', 'top_10'),
('Harvard University', 3, 'USA', 'top_10'),
('UC Berkeley', 15, 'USA', 'top_20'),
('Carnegie Mellon University', 25, 'USA', 'top_50'),
('University of Toronto', 35, 'Canada', 'top_50'),
('ETH Zurich', 8, 'Switzerland', 'top_10'),
('Tsinghua University', 20, 'China', 'top_50'),
('Peking University', 18, 'China', 'top_50'),
('National University of Singapore', 30, 'Singapore', 'top_50')
ON CONFLICT (university) DO NOTHING;

-- Insert sample major relations
INSERT INTO major_relations (major1, major2, relation_type, similarity_score) VALUES
('Computer Science', 'Software Engineering', 'related', 0.9),
('Computer Science', 'Data Science', 'related', 0.8),
('Computer Science', 'Artificial Intelligence', 'subcategory', 0.9),
('Electrical Engineering', 'Computer Engineering', 'related', 0.8),
('Business Administration', 'Management', 'related', 0.9),
('Business Administration', 'Marketing', 'subcategory', 0.7),
('Psychology', 'Cognitive Science', 'related', 0.8),
('Biology', 'Biotechnology', 'related', 0.8),
('Mathematics', 'Statistics', 'related', 0.8),
('Physics', 'Engineering Physics', 'related', 0.7)
ON CONFLICT (major1, major2) DO NOTHING;

-- Insert sample major categories
INSERT INTO major_categories (major, category, subcategory) VALUES
('Computer Science', 'STEM', 'Computer & Information Sciences'),
('Software Engineering', 'STEM', 'Computer & Information Sciences'),
('Data Science', 'STEM', 'Computer & Information Sciences'),
('Electrical Engineering', 'STEM', 'Engineering'),
('Mechanical Engineering', 'STEM', 'Engineering'),
('Business Administration', 'Business', 'Management'),
('Marketing', 'Business', 'Marketing & Sales'),
('Finance', 'Business', 'Finance & Accounting'),
('Psychology', 'Social Sciences', 'Psychology & Behavioral Sciences'),
('Biology', 'STEM', 'Life Sciences'),
('Chemistry', 'STEM', 'Physical Sciences'),
('Mathematics', 'STEM', 'Mathematics & Statistics'),
('Physics', 'STEM', 'Physical Sciences'),
('Economics', 'Social Sciences', 'Economics')
ON CONFLICT (major, category) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_university_rankings_university ON university_rankings(university);
CREATE INDEX IF NOT EXISTS idx_university_rankings_ranking ON university_rankings(ranking);
CREATE INDEX IF NOT EXISTS idx_major_relations_major1 ON major_relations(major1);
CREATE INDEX IF NOT EXISTS idx_major_relations_major2 ON major_relations(major2);
CREATE INDEX IF NOT EXISTS idx_major_categories_major ON major_categories(major);
CREATE INDEX IF NOT EXISTS idx_major_categories_category ON major_categories(category);
