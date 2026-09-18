-- Dummy property data export
-- Run against production db.sqlite3 (same schema)
BEGIN TRANSACTION;

-- Amenities
INSERT INTO listings_amenity (id, name) VALUES (1, 'Swimming Pool');
INSERT INTO listings_amenity (id, name) VALUES (2, 'Garage');
INSERT INTO listings_amenity (id, name) VALUES (3, 'Garden');
INSERT INTO listings_amenity (id, name) VALUES (4, 'Air Conditioning');
INSERT INTO listings_amenity (id, name) VALUES (5, 'Balcony');

-- Properties
INSERT INTO listings_property (id, title, slug, listing_type, property_type, status, price, address, city, bedrooms, bathrooms, area_sqft, description, map_link, is_featured, created_at, updated_at, latitude, longitude, state) VALUES (1, 'Family House', 'family-house', 'sale', 'house', 'available', 450000, '12 Oak Street', 'Springfield', 4, 3, 2400, 'A spacious modern family house with an open-plan kitchen and large backyard.', '', 1, '2026-09-02 15:56:15.978072', '2026-09-12 14:51:30.317897', NULL, NULL, '');
INSERT INTO listings_property (id, title, slug, listing_type, property_type, status, price, address, city, bedrooms, bathrooms, area_sqft, description, map_link, is_featured, created_at, updated_at, latitude, longitude, state) VALUES (2, 'Downtown Luxury Apartment', 'downtown-luxury-apartment', 'rent', 'apartment', 'available', 2200, '88 Central Ave', 'Springfield', 2, 2, 1100, 'Stylish apartment in the heart of downtown, walking distance to everything.', '', 1, '2026-09-02 15:56:15.987764', '2026-09-02 15:56:15.987790', NULL, NULL, '');
INSERT INTO listings_property (id, title, slug, listing_type, property_type, status, price, address, city, bedrooms, bathrooms, area_sqft, description, map_link, is_featured, created_at, updated_at, latitude, longitude, state) VALUES (3, 'Countryside Villa', 'countryside-villa', 'sale', 'villa', 'available', 890000, '4 Hilltop Road', 'Greenfield', 5, 4, 3800, 'An elegant villa surrounded by nature, perfect for a quiet family life.', '', 1, '2026-09-02 15:56:15.996459', '2026-09-02 15:56:15.996477', NULL, NULL, '');
INSERT INTO listings_property (id, title, slug, listing_type, property_type, status, price, address, city, bedrooms, bathrooms, area_sqft, description, map_link, is_featured, created_at, updated_at, latitude, longitude, state) VALUES (4, 'Cozy Studio Apartment', 'cozy-studio-apartment', 'rent', 'apartment', 'available', 1200, '21 Elm Street', 'Springfield', 1, 1, 550, 'Compact and cozy studio, ideal for a single professional or student.', '', 0, '2026-09-02 15:56:16.006157', '2026-09-02 15:56:16.006185', NULL, NULL, '');
INSERT INTO listings_property (id, title, slug, listing_type, property_type, status, price, address, city, bedrooms, bathrooms, area_sqft, description, map_link, is_featured, created_at, updated_at, latitude, longitude, state) VALUES (5, 'Commercial Office Space', 'commercial-office-space', 'rent', 'commercial', 'available', 3500, '500 Business Park', 'Greenfield', 0, 2, 2000, 'Prime office space with parking, ready to move in.', '', 0, '2026-09-02 15:56:16.014362', '2026-09-02 15:56:16.014379', NULL, NULL, '');
INSERT INTO listings_property (id, title, slug, listing_type, property_type, status, price, address, city, bedrooms, bathrooms, area_sqft, description, map_link, is_featured, created_at, updated_at, latitude, longitude, state) VALUES (6, 'Residential Plot', 'residential-plot', 'sale', 'plot', 'available', 150000, 'Lot 7, River Road', 'Riverside', 0, 0, 6000, 'Great investment opportunity, residential plot near the river.', '', 0, '2026-09-02 15:56:16.022332', '2026-09-12 15:28:57.271755', NULL, NULL, '');

-- Property <-> Amenity relations
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (1, 1, 1);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (2, 1, 2);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (3, 1, 3);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (4, 2, 1);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (5, 2, 2);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (6, 2, 3);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (7, 3, 1);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (8, 3, 2);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (9, 3, 3);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (10, 4, 1);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (11, 4, 2);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (12, 4, 3);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (13, 5, 1);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (14, 5, 2);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (15, 5, 3);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (16, 6, 1);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (17, 6, 2);
INSERT INTO listings_property_amenities (id, property_id, amenity_id) VALUES (18, 6, 3);

COMMIT;
