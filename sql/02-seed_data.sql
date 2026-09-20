-- Seed data for travel booking agent
-- Run after tables.sql

-- ============================================================
-- Airports
-- ============================================================
INSERT INTO airports (iata_code, name, city, country, timezone) VALUES
('JFK', 'John F. Kennedy International Airport', 'New York', 'United States', 'America/New_York'),
('LAX', 'Los Angeles International Airport', 'Los Angeles', 'United States', 'America/Los_Angeles'),
('ORD', 'O''Hare International Airport', 'Chicago', 'United States', 'America/Chicago'),
('ATL', 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'United States', 'America/New_York'),
('DFW', 'Dallas/Fort Worth International Airport', 'Dallas', 'United States', 'America/Chicago'),
('SFO', 'San Francisco International Airport', 'San Francisco', 'United States', 'America/Los_Angeles'),
('MIA', 'Miami International Airport', 'Miami', 'United States', 'America/New_York'),
('SEA', 'Seattle-Tacoma International Airport', 'Seattle', 'United States', 'America/Los_Angeles'),
('BOS', 'Boston Logan International Airport', 'Boston', 'United States', 'America/New_York'),
('DEN', 'Denver International Airport', 'Denver', 'United States', 'America/Denver'),
('LHR', 'Heathrow Airport', 'London', 'United Kingdom', 'Europe/London'),
('CDG', 'Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris'),
('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany', 'Europe/Berlin'),
('NRT', 'Narita International Airport', 'Tokyo', 'Japan', 'Asia/Tokyo'),
('DXB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates', 'Asia/Dubai');

-- ============================================================
-- Airlines
-- ============================================================
INSERT INTO airlines (iata_code, name) VALUES
('AA', 'American Airlines'),
('DL', 'Delta Air Lines'),
('UA', 'United Airlines'),
('BA', 'British Airways'),
('LH', 'Lufthansa'),
('EK', 'Emirates'),
('JL', 'Japan Airlines');

-- ============================================================
-- Flights
-- ============================================================

-- JFK <-> LAX (direct)
INSERT INTO flights (flight_id, airline_code, flight_number, departure_airport, arrival_airport, departure_time, arrival_time, duration_minutes, cabin_class, base_price, available_seats) VALUES
(1,  'AA', 'AA100', 'JFK', 'LAX', '2026-10-15 08:00:00-04', '2026-10-15 11:30:00-07', 330, 'economy',  249.00, 120),
(2,  'AA', 'AA100', 'JFK', 'LAX', '2026-10-15 08:00:00-04', '2026-10-15 11:30:00-07', 330, 'business', 789.00,  24),
(3,  'DL', 'DL402', 'JFK', 'LAX', '2026-10-15 12:00:00-04', '2026-10-15 15:20:00-07', 320, 'economy',  279.00, 140),
(4,  'UA', 'UA205', 'JFK', 'LAX', '2026-10-15 18:00:00-04', '2026-10-15 21:10:00-07', 310, 'economy',  219.00, 110),
(5,  'DL', 'DL411', 'LAX', 'JFK', '2026-10-16 07:00:00-07', '2026-10-16 15:20:00-04', 320, 'economy',  259.00, 130),
(6,  'AA', 'AA101', 'LAX', 'JFK', '2026-10-16 14:00:00-07', '2026-10-16 22:30:00-04', 330, 'economy',  269.00, 115),

-- JFK <-> ORD
(7,  'AA', 'AA300', 'JFK', 'ORD', '2026-10-15 09:00:00-04', '2026-10-15 11:15:00-05', 135, 'economy',  179.00, 150),
(8,  'UA', 'UA510', 'JFK', 'ORD', '2026-10-15 15:00:00-04', '2026-10-15 17:10:00-05', 130, 'economy',  169.00, 140),
(9,  'UA', 'UA511', 'ORD', 'JFK', '2026-10-16 10:00:00-05', '2026-10-16 14:05:00-04', 125, 'economy',  175.00, 135),

-- ORD <-> LAX
(10, 'UA', 'UA720', 'ORD', 'LAX', '2026-10-15 13:00:00-05', '2026-10-15 15:15:00-07', 255, 'economy',  199.00, 130),
(11, 'AA', 'AA340', 'ORD', 'LAX', '2026-10-15 17:00:00-05', '2026-10-15 19:10:00-07', 250, 'economy',  189.00, 125),

-- JFK <-> LHR
(12, 'BA', 'BA178', 'JFK', 'LHR', '2026-10-15 20:00:00-04', '2026-10-16 08:00:00+00', 420, 'economy',  449.00,  80),
(13, 'BA', 'BA178', 'JFK', 'LHR', '2026-10-15 20:00:00-04', '2026-10-16 08:00:00+00', 420, 'business', 1899.00, 20),
(14, 'AA', 'AA106', 'JFK', 'LHR', '2026-10-15 22:00:00-04', '2026-10-16 10:10:00+00', 430, 'economy',  479.00,  90),
(15, 'BA', 'BA179', 'LHR', 'JFK', '2026-10-16 11:00:00+00', '2026-10-16 14:15:00-04', 435, 'economy',  469.00,  85),

-- LHR <-> CDG
(16, 'BA', 'BA304', 'LHR', 'CDG', '2026-10-16 10:00:00+00', '2026-10-16 12:15:00+01',  75, 'economy',  129.00, 100),
(17, 'BA', 'BA305', 'CDG', 'LHR', '2026-10-16 14:00:00+01', '2026-10-16 14:15:00+00',  75, 'economy',  129.00,  95),

-- LHR <-> FRA
(18, 'LH', 'LH901', 'LHR', 'FRA', '2026-10-16 09:30:00+00', '2026-10-16 12:00:00+01', 90, 'economy',  139.00, 110),
(19, 'LH', 'LH902', 'FRA', 'LHR', '2026-10-16 15:00:00+01', '2026-10-16 15:30:00+00', 90, 'economy',  139.00, 105),

-- JFK -> CDG (via LHR, connecting)
-- Uses flights 12 (JFK->LHR) + 16 (LHR->CDG)

-- LAX <-> SFO
(20, 'UA', 'UA850', 'LAX', 'SFO', '2026-10-15 07:00:00-07', '2026-10-15 08:25:00-07',  85, 'economy',   99.00, 160),
(21, 'DL', 'DL660', 'LAX', 'SFO', '2026-10-15 14:00:00-07', '2026-10-15 15:20:00-07',  80, 'economy',  109.00, 145),
(22, 'UA', 'UA851', 'SFO', 'LAX', '2026-10-16 09:00:00-07', '2026-10-16 10:30:00-07',  90, 'economy',  105.00, 150),

-- ATL <-> MIA
(23, 'DL', 'DL230', 'ATL', 'MIA', '2026-10-15 10:00:00-04', '2026-10-15 12:00:00-04', 120, 'economy',  149.00, 130),
(24, 'DL', 'DL231', 'MIA', 'ATL', '2026-10-16 08:00:00-04', '2026-10-16 10:05:00-04', 125, 'economy',  155.00, 125),

-- JFK <-> MIA
(25, 'AA', 'AA550', 'JFK', 'MIA', '2026-10-15 07:30:00-04', '2026-10-15 10:45:00-04', 195, 'economy',  189.00, 120),
(26, 'DL', 'DL770', 'JFK', 'MIA', '2026-10-15 16:00:00-04', '2026-10-15 19:10:00-04', 190, 'economy',  199.00, 110),
(27, 'AA', 'AA551', 'MIA', 'JFK', '2026-10-16 11:00:00-04', '2026-10-16 14:15:00-04', 195, 'economy',  195.00, 115),

-- DFW <-> LAX
(28, 'AA', 'AA440', 'DFW', 'LAX', '2026-10-15 11:00:00-05', '2026-10-15 12:30:00-07', 210, 'economy',  179.00, 135),
(29, 'AA', 'AA441', 'LAX', 'DFW', '2026-10-16 13:00:00-07', '2026-10-16 18:00:00-05', 200, 'economy',  175.00, 130),

-- JFK <-> DFW
(30, 'AA', 'AA350', 'JFK', 'DFW', '2026-10-15 08:30:00-04', '2026-10-15 11:30:00-05', 240, 'economy',  209.00, 120),
(31, 'AA', 'AA351', 'DFW', 'JFK', '2026-10-16 09:00:00-05', '2026-10-16 15:00:00-04', 240, 'economy',  215.00, 118),

-- BOS <-> SFO
(32, 'UA', 'UA630', 'BOS', 'SFO', '2026-10-15 08:00:00-04', '2026-10-15 11:45:00-07', 345, 'economy',  289.00, 100),
(33, 'UA', 'UA631', 'SFO', 'BOS', '2026-10-16 10:00:00-07', '2026-10-16 18:30:00-04', 330, 'economy',  279.00,  95),

-- DEN <-> SEA
(34, 'UA', 'UA460', 'DEN', 'SEA', '2026-10-15 09:00:00-06', '2026-10-15 11:00:00-07', 180, 'economy',  159.00, 140),
(35, 'UA', 'UA461', 'SEA', 'DEN', '2026-10-16 07:30:00-07', '2026-10-16 11:15:00-06', 165, 'economy',  149.00, 135),

-- DXB <-> LHR
(36, 'EK', 'EK001', 'DXB', 'LHR', '2026-10-15 08:00:00+04', '2026-10-15 12:30:00+00', 450, 'economy',  399.00,  90),
(37, 'EK', 'EK001', 'DXB', 'LHR', '2026-10-15 08:00:00+04', '2026-10-15 12:30:00+00', 450, 'first',   2499.00,  8),
(38, 'EK', 'EK002', 'LHR', 'DXB', '2026-10-16 14:00:00+00', '2026-10-17 00:30:00+04', 450, 'economy',  419.00,  85),

-- NRT <-> LAX
(39, 'JL', 'JL062', 'NRT', 'LAX', '2026-10-15 17:00:00+09', '2026-10-15 11:00:00-07', 600, 'economy',  599.00,  70),
(40, 'JL', 'JL062', 'NRT', 'LAX', '2026-10-15 17:00:00+09', '2026-10-15 11:00:00-07', 600, 'business', 2199.00, 16),
(41, 'JL', 'JL061', 'LAX', 'NRT', '2026-10-16 12:00:00-07', '2026-10-17 16:30:00+09', 630, 'economy',  629.00,  65);

-- Reset the flight_id sequence
SELECT setval('flights_flight_id_seq', (SELECT MAX(flight_id) FROM flights));

-- ============================================================
-- Routes (direct flights)
-- ============================================================
INSERT INTO routes (route_id, departure_airport, arrival_airport, total_duration, total_price, num_stops) VALUES
-- JFK -> LAX direct
(1,  'JFK', 'LAX', 330,  249.00, 0),
(2,  'JFK', 'LAX', 330,  789.00, 0),
(3,  'JFK', 'LAX', 320,  279.00, 0),
(4,  'JFK', 'LAX', 310,  219.00, 0),
-- LAX -> JFK direct
(5,  'LAX', 'JFK', 320,  259.00, 0),
(6,  'LAX', 'JFK', 330,  269.00, 0),
-- JFK -> ORD direct
(7,  'JFK', 'ORD', 135,  179.00, 0),
(8,  'JFK', 'ORD', 130,  169.00, 0),
-- ORD -> JFK direct
(9,  'ORD', 'JFK', 125,  175.00, 0),
-- JFK -> LHR direct
(10, 'JFK', 'LHR', 420,  449.00, 0),
(11, 'JFK', 'LHR', 420, 1899.00, 0),
(12, 'JFK', 'LHR', 430,  479.00, 0),
-- LHR -> JFK direct
(13, 'LHR', 'JFK', 435,  469.00, 0),
-- LAX -> SFO direct
(14, 'LAX', 'SFO',  85,   99.00, 0),
(15, 'LAX', 'SFO',  80,  109.00, 0),
-- SFO -> LAX direct
(16, 'SFO', 'LAX',  90,  105.00, 0),
-- ATL -> MIA direct
(17, 'ATL', 'MIA', 120,  149.00, 0),
-- MIA -> ATL direct
(18, 'MIA', 'ATL', 125,  155.00, 0),
-- JFK -> MIA direct
(19, 'JFK', 'MIA', 195,  189.00, 0),
(20, 'JFK', 'MIA', 190,  199.00, 0),
-- MIA -> JFK direct
(21, 'MIA', 'JFK', 195,  195.00, 0),
-- DFW -> LAX direct
(22, 'DFW', 'LAX', 210,  179.00, 0),
-- LAX -> DFW direct
(23, 'LAX', 'DFW', 200,  175.00, 0),
-- JFK -> DFW direct
(24, 'JFK', 'DFW', 240,  209.00, 0),
-- DFW -> JFK direct
(25, 'DFW', 'JFK', 240,  215.00, 0),
-- BOS -> SFO direct
(26, 'BOS', 'SFO', 345,  289.00, 0),
-- SFO -> BOS direct
(27, 'SFO', 'BOS', 330,  279.00, 0),
-- DEN -> SEA direct
(28, 'DEN', 'SEA', 180,  159.00, 0),
-- SEA -> DEN direct
(29, 'SEA', 'DEN', 165,  149.00, 0),
-- DXB -> LHR direct
(30, 'DXB', 'LHR', 450,  399.00, 0),
(31, 'DXB', 'LHR', 450, 2499.00, 0),
-- LHR -> DXB direct
(32, 'LHR', 'DXB', 450,  419.00, 0),
-- NRT -> LAX direct
(33, 'NRT', 'LAX', 600,  599.00, 0),
(34, 'NRT', 'LAX', 600, 2199.00, 0),
-- LAX -> NRT direct
(35, 'LAX', 'NRT', 630,  629.00, 0),
-- LHR -> CDG direct
(36, 'LHR', 'CDG',  75,  129.00, 0),
-- CDG -> LHR direct
(37, 'CDG', 'LHR',  75,  129.00, 0),
-- LHR -> FRA direct
(38, 'LHR', 'FRA',  90,  139.00, 0),
-- FRA -> LHR direct
(39, 'FRA', 'LHR',  90,  139.00, 0),

-- ============================================================
-- Routes (connecting flights — 1 stop)
-- ============================================================
-- JFK -> LAX via ORD (AA300 + AA340): 135 + 120 layover + 250 = 505 min
(40, 'JFK', 'LAX', 505,  368.00, 1),
-- JFK -> LAX via ORD (UA510 + UA720): not same day feasible, skip
-- JFK -> CDG via LHR (BA178 + BA304): 420 + 120 layover + 75 = 615 min
(41, 'JFK', 'CDG', 615,  578.00, 1),
-- JFK -> FRA via LHR (BA178 + LH901): 420 + 90 layover + 90 = 600 min
(42, 'JFK', 'FRA', 600,  588.00, 1),
-- JFK -> LAX via DFW (AA350 + AA440): 240 + 90 layover + 210 = 540 min
(43, 'JFK', 'LAX', 540,  388.00, 1),
-- JFK -> SFO via LAX (AA100 + UA850): not same day feasible with timing
-- DXB -> CDG via LHR (EK001 + BA304): 450 + layover + 75 min
(44, 'DXB', 'CDG', 600,  528.00, 1),
-- DXB -> FRA via LHR (EK001 + LH901): not feasible timing (arrives 12:30, departs 09:30)
-- NRT -> SFO via LAX (JL062 + reverse not available same day)
-- ORD -> LAX direct
(45, 'ORD', 'LAX', 255,  199.00, 0),
(46, 'ORD', 'LAX', 250,  189.00, 0);

-- Reset the route_id sequence
SELECT setval('routes_route_id_seq', (SELECT MAX(route_id) FROM routes));

-- ============================================================
-- Route Flights (junction table)
-- ============================================================
INSERT INTO route_flights (route_id, flight_id, leg_order) VALUES
-- Direct routes
(1,  1,  1),   -- JFK->LAX AA100 economy
(2,  2,  1),   -- JFK->LAX AA100 business
(3,  3,  1),   -- JFK->LAX DL402 economy
(4,  4,  1),   -- JFK->LAX UA205 economy
(5,  5,  1),   -- LAX->JFK DL411
(6,  6,  1),   -- LAX->JFK AA101
(7,  7,  1),   -- JFK->ORD AA300
(8,  8,  1),   -- JFK->ORD UA510
(9,  9,  1),   -- ORD->JFK UA511
(10, 12, 1),   -- JFK->LHR BA178 economy
(11, 13, 1),   -- JFK->LHR BA178 business
(12, 14, 1),   -- JFK->LHR AA106 economy
(13, 15, 1),   -- LHR->JFK BA179
(14, 20, 1),   -- LAX->SFO UA850
(15, 21, 1),   -- LAX->SFO DL660
(16, 22, 1),   -- SFO->LAX UA851
(17, 23, 1),   -- ATL->MIA DL230
(18, 24, 1),   -- MIA->ATL DL231
(19, 25, 1),   -- JFK->MIA AA550
(20, 26, 1),   -- JFK->MIA DL770
(21, 27, 1),   -- MIA->JFK AA551
(22, 28, 1),   -- DFW->LAX AA440
(23, 29, 1),   -- LAX->DFW AA441
(24, 30, 1),   -- JFK->DFW AA350
(25, 31, 1),   -- DFW->JFK AA351
(26, 32, 1),   -- BOS->SFO UA630
(27, 33, 1),   -- SFO->BOS UA631
(28, 34, 1),   -- DEN->SEA UA460
(29, 35, 1),   -- SEA->DEN UA461
(30, 36, 1),   -- DXB->LHR EK001 economy
(31, 37, 1),   -- DXB->LHR EK001 first
(32, 38, 1),   -- LHR->DXB EK002
(33, 39, 1),   -- NRT->LAX JL062 economy
(34, 40, 1),   -- NRT->LAX JL062 business
(35, 41, 1),   -- LAX->NRT JL061
(36, 16, 1),   -- LHR->CDG BA304
(37, 17, 1),   -- CDG->LHR BA305
(38, 18, 1),   -- LHR->FRA LH901
(39, 19, 1),   -- FRA->LHR LH902
-- Connecting routes
(40, 7,  1),   -- JFK->ORD AA300 (leg 1 of JFK->LAX via ORD)
(40, 11, 2),   -- ORD->LAX AA340 (leg 2)
(41, 12, 1),   -- JFK->LHR BA178 (leg 1 of JFK->CDG via LHR)
(41, 16, 2),   -- LHR->CDG BA304 (leg 2)
(42, 12, 1),   -- JFK->LHR BA178 (leg 1 of JFK->FRA via LHR)
(42, 18, 2),   -- LHR->FRA LH901 (leg 2)
(43, 30, 1),   -- JFK->DFW AA350 (leg 1 of JFK->LAX via DFW)
(43, 28, 2),   -- DFW->LAX AA440 (leg 2)
(44, 36, 1),   -- DXB->LHR EK001 (leg 1 of DXB->CDG via LHR)
(44, 16, 2),   -- LHR->CDG BA304 (leg 2)
(45, 10, 1),   -- ORD->LAX UA720
(46, 11, 1);   -- ORD->LAX AA340
