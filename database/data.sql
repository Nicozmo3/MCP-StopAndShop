CREATE DATABASE IF NOT EXISTS stopandshop;
USE stopandshop;

-- -----------------------------
-- Tables
-- -----------------------------

CREATE TABLE account (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    username VARCHAR(255),
    password_hash VARCHAR(255),
    created_at DATETIME
);

CREATE TABLE brand (
    brand_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255)
);

CREATE TABLE belief (
    belief_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    emoji VARCHAR(10),
    is_official BOOLEAN
);

CREATE TABLE brand_tag (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    tag_type VARCHAR(255)
);

CREATE TABLE brand_tags (
    brand_id INT,
    tag_id INT,
    PRIMARY KEY (brand_id, tag_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id),
    FOREIGN KEY (tag_id) REFERENCES brand_tag(tag_id)
);

CREATE TABLE brand_location (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    latitude FLOAT,
    longitude FLOAT,
    name VARCHAR(255),
    address VARCHAR(255),
    city VARCHAR(255),
    postal_code VARCHAR(20),
    brand_id INT,
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id)
);

CREATE TABLE brand_score (
    brand_id INT,
    belief_id INT,
    official_score INT,
    community_score INT,
    PRIMARY KEY (brand_id, belief_id),
    FOREIGN KEY (brand_id) REFERENCES brand(brand_id),
    FOREIGN KEY (belief_id) REFERENCES belief(belief_id)
);

CREATE TABLE petition (
    petition_id INT PRIMARY KEY,
    initiator_id INT,
    description TEXT,
    title VARCHAR(255),
    emoji VARCHAR(10),
    start_date DATETIME,
    initiator_anonymous BOOLEAN,
    signatures INT,
    FOREIGN KEY (initiator_id) REFERENCES account(account_id)
);

CREATE TABLE comment (
    comment_id INT PRIMARY KEY,
    author_id INT,
    concerned_brand_id INT,
    concerned_belief_id INT,
    text TEXT,
    note INT,
    is_anonymous BOOLEAN,
    created_at DATETIME,
    upvote_count INT,
    downvote_count INT,
    FOREIGN KEY (author_id) REFERENCES account(account_id),
    FOREIGN KEY (concerned_brand_id) REFERENCES brand(brand_id),
    FOREIGN KEY (concerned_belief_id) REFERENCES belief(belief_id)
);

CREATE TABLE comment_reaction (
    account_id INT,
    comment_id INT,
    is_upvote BOOLEAN,
    PRIMARY KEY (account_id, comment_id),
    FOREIGN KEY (account_id) REFERENCES account(account_id),
    FOREIGN KEY (comment_id) REFERENCES comment(comment_id)
);


INSERT INTO belief (title, description, emoji, is_official)
VALUES ('Management', 'Respect des employé dans les enseignes', '👥', true),
       ('Innovation ethique', 'innove en respectant les droits humains', '💡', true),
       ('Service Client', 'Niveau de service après vente et de support client', '📞', true),
       ('Respect des animaux', 'Respect les animaux', '🐾', true),
       ('Respect de l environnement', 'respect de l environement durant la production et l utilisation du produit',
        '🌍', true),
       ('Guerre en Ukraine', 'Prend position sur la guerre en Ukraine', '🇺🇦', false),
       ('Diversité et inclusion', 'Favorise la diversité et l inclusion', '🤝', true);

INSERT INTO account (email, username, password_hash, created_at)
VALUES ('alice@test.com', 'alice', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('bob@test.com', 'bob', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('charlie@test.com', 'charlie', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('david@test.com', 'david', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('emma@test.com', 'emma', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('frank@test.com', 'frank', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('grace@test.com', 'grace', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('henry@test.com', 'henry', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('isabella@test.com', 'isabella', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('jack@test.com', 'jack', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('kate@test.com', 'kate', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('leo@test.com', 'leo', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('mia@test.com', 'mia', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('noah@test.com', 'noah', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW()),
       ('olivia@test.com', 'olivia', '$2a$10$7eqJtq98hPqEX7fNZaFWoOa8dM.9vYH3Uu1rZtGqQf6gWQKp9G6eW', NOW());

INSERT INTO brand_tag (tag_type)
VALUES ('Epicerie'),
       ('Sport'),
       ('Vêtements'),
       ('High-Tech'),
       ('Cosmétiques'),
       ('Outdoor');

INSERT INTO brand (name)
VALUES ('Patagonia'),
       ('Carrefour'),
       ('Lush'),
       ('Fnac'),
       ('Decathlon'),
       ('Celio'),
       ('Monoprix');

INSERT INTO brand_tags (brand_id, tag_id)
VALUES (1, 6),
       (2, 1),
       (3, 5),
       (4, 4),
       (5, 2),
       (6, 3),
       (7, 1);

INSERT INTO brand_location (latitude, longitude, name, address, city, postal_code, brand_id)
VALUES (48.8566, 2.3522, 'Carrefour Marais', '52 rue de Turenne', 'Paris', '75003', 2),
       (48.8424, 2.3389, 'Carrefour 13ème', '89 Avenue d''Italie', 'Paris', '75013', 2),
       (48.8945, 2.2931, 'Carrefour Montmartre', '123 Boulevard de Clichy', 'Paris', '75018', 2),
       (48.8404, 2.2869, 'Carrefour Montparnasse', '50 Rue Falguière', 'Paris', '75015', 2),

       (48.8210, 2.2844, 'Decathlon Paris Bercy', '15 Avenue des Andes', 'Paris', '75012', 5),
       (48.8834, 2.3667, 'Decathlon Canal St-Martin', '76 Quai de la Loire', 'Paris', '75019', 5),

       (48.8729, 2.3388, 'Fnac Opéra', '26 avenue de l''Opéra', 'Paris', '75001', 4),
       (48.8509, 2.3551, 'Fnac Saint-Denis', '111 rue Saint-Denis', 'Paris', '75002', 4),

       (48.8626, 2.3465, 'Lush Marais', '100 rue Vieille du Temple', 'Paris', '75003', 3),
       (48.8738, 2.2972, 'Lush Champs-Élysées', '34 Avenue des Champs-Élysées', 'Paris', '75008', 3),

       (48.8566, 2.3467, 'Monoprix Île Saint-Louis', '45 rue Saint-Louis en l''Île', 'Paris', '75004', 7),
       (48.8848, 2.3425, 'Monoprix Belleville', '78 rue de Belleville', 'Paris', '75020', 7),

       (48.8738, 2.2972, 'Celio Champs-Élysées', '89 Avenue des Champs-Élysées', 'Paris', '75008', 6),
       (48.8728, 2.3388, 'Celio Palais Royal', '12 rue Saint-Honoré', 'Paris', '75001', 6),

       (48.8632, 2.2922, 'Patagonia Saint-Germain', '23 rue Bonaparte', 'Paris', '75006', 1),
       (48.8750, 2.2968, 'Patagonia Invalides', '5 avenue Bosquet', 'Paris', '75007', 1);


INSERT INTO brand_score (brand_id, belief_id, official_score, community_score)
VALUES ('1', '1', 9, 8),
       ('1', '2', 10, 9),
       ('1', '3', 8, 7),
       ('1', '4', 10, 9),
       ('1', '5', 10, 9),
       ('1', '6', 8, 7),
       ('1', '7', 9, 8),

       ('2', '1', 6, 5),
       ('2', '2', 5, 4),
       ('2', '3', 7, 6),
       ('2', '4', 4, 3),
       ('2', '5', 5, 4),
       ('2', '6', 6, 5),
       ('2', '7', 6, 5),

       ('3', '1', 4, 2),
       ('3', '2', 9, 8),
       ('3', '3', 7, 6),
       ('3', '4', 10, 9),
       ('3', '5', 8, 7),
       ('3', '6', 7, 6),
       ('3', '7', 8, 7),

       ('4', '1', 7, 6),
       ('4', '2', 6, 5),
       ('4', '3', 8, 7),
       ('4', '4', 5, 4),
       ('4', '5', 6, 5),
       ('4', '6', 7, 6),
       ('4', '7', 7, 6),

       ('5', '1', 7, 6),
       ('5', '2', 6, 5),
       ('5', '3', 8, 7),
       ('5', '4', 5, 4),
       ('5', '5', 6, 5),
       ('5', '6', 7, 6),
       ('5', '7', 7, 6);

INSERT INTO petition
(petition_id, initiator_id, description, title, emoji, start_date, initiator_anonymous, signatures)
VALUES (1, 1, 'Plant 10,000 trees in urban areas to reduce pollution and improve air quality.',
        'Urban Tree Planting Initiative', '🌳', '2024-01-15 10:00:00', FALSE, 1789),

       (2, 2, 'Introduce stricter penalties for illegal dumping in protected natural areas.',
        'Stop Illegal Dumping Now', '🚫', '2024-02-02 09:30:00', FALSE, 1515),

       (3, 3, 'Provide free public transport on weekends to reduce traffic congestion.',
        'Free Weekend Public Transport', '🚌', '2024-03-10 14:00:00', FALSE, 751),

       (4, 4, 'Ban single-use plastic bags in all supermarkets nationwide.',
        'Ban Single-Use Plastics', '🛍️', '2024-01-25 08:45:00', TRUE, 456),

       (5, 1, 'Increase funding for public hospitals to improve patient care quality.',
        'Support Public Hospitals', '🏥', '2024-02-18 16:20:00', FALSE, 5151),

       (6, 5, 'Build more bicycle lanes to promote eco-friendly commuting.',
        'Expand Bicycle Infrastructure', '🚲', '2024-03-05 11:15:00', FALSE, 5419),

       (7, 2, 'Reduce university tuition fees by 20% for public institutions.',
        'Lower University Tuition Fees', '🎓', '2024-04-01 13:40:00', FALSE, 6748),

       (8, 3, 'Create more green public spaces in suburban neighborhoods.',
        'More Green Spaces for Communities', '🌿', '2024-01-12 17:10:00', TRUE, 9999),

       (9, 4, 'Implement renewable energy solutions in all public buildings.',
        'Renewable Energy for Public Buildings', '☀️', '2024-02-27 12:00:00', FALSE, 980),

       (10, 5, 'Increase minimum wage to match inflation rates.',
        'Fair Minimum Wage Adjustment', '💰', '2024-03-22 09:00:00', FALSE, 3),

       (11, 1, 'Improve road safety measures near schools and playgrounds.',
        'Safer Roads for Children', '🚦', '2024-04-15 10:30:00', FALSE, 999),

       (12, 2, 'Support small local farmers with tax reductions.',
        'Tax Relief for Local Farmers', '🌾', '2024-05-01 15:45:00', FALSE, 257),

       (13, 3, 'Introduce mandatory recycling programs in all municipalities.',
        'Mandatory Recycling Nationwide', '♻️', '2024-01-08 11:00:00', TRUE, 999),

       (14, 4, 'Subsidize solar panel installation for private households.',
        'Solar Panels for Everyone', '🔋', '2024-02-14 10:00:00', FALSE, 345),

       (15, 5, 'Strengthen laws protecting endangered wildlife species.',
        'Protect Endangered Wildlife', '🦁', '2024-03-18 16:00:00', FALSE, 4444),

       (16, 1, 'Provide free mental health services for students.',
        'Mental Health Support for Students', '🧠', '2024-04-05 13:00:00', FALSE, 8888),

       (17, 2, 'Increase transparency in government spending.',
        'Government Spending Transparency Act', '📊', '2024-05-10 09:00:00', FALSE, 1290),

       (18, 3, 'Install more public electric vehicle charging stations.',
        'EV Charging Infrastructure Expansion', '🔌', '2024-01-30 12:30:00', FALSE, 3737),

       (19, 4, 'Reduce property taxes for first-time home buyers.',
        'Support First-Time Home Buyers', '🏠', '2024-02-09 14:15:00', TRUE, 3455),

       (20, 5, 'Create community programs to reduce youth unemployment.',
        'Youth Employment Initiative', '👷', '2024-03-27 11:45:00', FALSE, 7322);

INSERT INTO comment
(comment_id, author_id, concerned_brand_id, concerned_belief_id, text, note, is_anonymous, created_at, upvote_count,
 downvote_count)
VALUES (1, 1, 1, 5, 'Cette boutique fait beaucoup d efforts concrets pour limiter son impact environnemental.', 9,
        FALSE, '2024-04-03 10:15:00', 3, 0),
       (2, 2, 1, 6, 'La prise de position est visible, mais elle reste parfois trop marketing a mon gout.', 6, FALSE,
        '2024-04-10 14:20:00', 1, 1),
       (3, 3, 1, 3, 'Le service en magasin est agreable, mais le SAV n est pas toujours a la hauteur.', 7, TRUE,
        '2024-05-01 09:45:00', 2, 0),
       (4, 4, 2, 5, 'Cette boutique ne respecte pas l environnement et utilise encore trop d emballages.', 3, FALSE,
        '2024-04-18 18:05:00', 9, 2),
       (5, 5, 2, 1, 'Le management en rayon est tres inegal selon les equipes.', 5, FALSE, '2024-05-06 12:10:00', 2, 1),
       (6, 6, 2, 7, 'Des efforts visibles sur la diversite, mais il reste du chemin a faire.', 6, TRUE,
        '2024-05-19 16:30:00', 4, 11),
       (7, 7, 4, 2, 'J ai trouve la communication plus transparente que chez d autres enseignes.', 8, FALSE,
        '2024-04-27 11:40:00', 2, 0),
       (8, 8, 4, 3, 'Le service client est reactif et poli, tres bonne experience globale.', 9, FALSE,
        '2024-05-12 13:50:00', 5, 16),
       (9, 8, 2, 7, 'Nul', 0, TRUE, '2024-05-19 16:30:00', 0, 17),
       (10, 9, 1, 5, 'Des efforts reels sur les circuits courts, c est appreciable.', 8, FALSE, '2024-05-20 10:10:00',
        4, 0),
       (11, 10, 1, 6, 'On sent une volonte de bien faire mais tout n est pas encore coherent.', 6, TRUE,
        '2024-05-22 15:42:00', 2, 1),
       (12, 11, 1, 3, 'Personnel sympathique mais parfois deborde aux heures de pointe.', 7, FALSE,
        '2024-06-01 11:00:00', 3, 0),
       (13, 12, 2, 5, 'Aucune vraie politique environnementale visible en magasin.', 2, TRUE, '2024-05-25 09:20:00', 6,
        1),
       (14, 13, 2, 1, 'Organisation interne confuse, cela se ressent cote client.', 4, FALSE, '2024-06-02 14:10:00', 3,
        2),
       (15, 14, 2, 7, 'Bon debut sur l inclusion mais manque encore d actions concretes.', 5, TRUE,
        '2024-06-05 17:25:00', 2, 3),
       (16, 1, 3, 2, 'Communication claire et honnete, ca change.', 8, FALSE, '2024-05-11 10:00:00', 5, 0),
       (17, 2, 3, 4, 'Les produits sont de qualite mais assez chers.', 7, FALSE, '2024-05-18 13:30:00', 4, 1),
       (18, 3, 3, 6, 'Beaucoup de promesses mais peu de preuves concretes.', 5, TRUE, '2024-05-29 16:45:00', 2, 2),
       (19, 9, 4, 3, 'Experience client fluide, rien a redire.', 9, FALSE, '2024-06-03 12:15:00', 6, 0),
       (20, 10, 4, 2, 'Discours transparent mais parfois trop corporate.', 6, TRUE, '2024-06-04 09:50:00', 2, 1),
       (21, 1, 5, 5, 'Engagement environnemental tres faible selon moi.', 3, TRUE, '2024-05-14 08:30:00', 3, 4),
       (22, 2, 5, 1, 'Bonne ambiance en magasin, equipe agreable.', 8, FALSE, '2024-05-21 11:20:00', 5, 0),
       (23, 3, 5, 7, 'Efforts visibles sur la diversite, bravo.', 7, FALSE, '2024-05-28 15:10:00', 4, 1),
       (24, 4, 5, 6, 'Beaucoup de communication mais peu d actions reelles.', 4, TRUE, '2024-06-06 18:40:00', 2, 3),
       (25, 5, 6, 3, 'Service client lent mais efficace au final.', 6, FALSE, '2024-05-30 14:00:00', 3, 1),
       (26, 6, 6, 2, 'Bonne transparence sur les pratiques internes.', 8, FALSE, '2024-06-01 10:25:00', 5, 0),
       (27, 7, 6, 4, 'Prix eleves pour une qualite correcte.', 6, TRUE, '2024-06-03 17:00:00', 2, 2),
       (28, 8, 7, 5, 'Tres bon engagement ecologique, continuez.', 9, FALSE, '2024-06-07 12:00:00', 6, 0),
       (29, 9, 7, 6, 'On dirait surtout du greenwashing.', 3, TRUE, '2024-06-08 09:35:00', 2, 5),
       (30, 10, 7, 1, 'Management efficace et equipe motivee.', 8, FALSE, '2024-06-09 16:20:00', 4, 0),
       (31, 11, 7, 3, 'Service correct sans etre exceptionnel.', 6, FALSE, '2024-06-10 11:10:00', 3, 1),
       (32, 12, 7, 7, 'Manque de representation dans les equipes.', 4, TRUE, '2024-06-11 14:45:00', 2, 3),
       (33, 13, 6, 2, 'Communication floue sur certains sujets.', 5, FALSE, '2024-06-12 18:05:00', 2, 2),
       (34, 14, 4, 4, 'Produits solides et durables.', 8, FALSE, '2024-06-13 10:50:00', 5, 0),
       (35, 1, 6, 6, 'Beaucoup de marketing, peu de fond.', 4, TRUE, '2024-06-14 13:15:00', 2, 3),
       (36, 2, 5, 5, 'Bon engagement global, encore perfectible.', 7, FALSE, '2024-06-15 15:30:00', 4, 1),
       (37, 15, 1, 5, 'lol', 1, TRUE, '2024-06-16 10:00:00', 0, 25),
       (38, 14, 1, 3, 'n importe quoi cette marque', 0, TRUE, '2024-06-16 10:05:00', 0, 30),

       (39, 13, 2, 1, 'je prefere les pizzas', 2, TRUE, '2024-06-16 10:10:00', 1, 22),
       (40, 12, 2, 7, 'c est nul nul nul nul', 0, TRUE, '2024-06-16 10:12:00', 0, 28),

       (41, 11, 3, 4, '???', 1, TRUE, '2024-06-16 10:15:00', 0, 18),
       (42, 10, 3, 6, 'mdr vous croyez vraiment a ca', 1, TRUE, '2024-06-16 10:18:00', 0, 21),

       (43, 9, 4, 2, 'first', 0, TRUE, '2024-06-16 10:20:00', 0, 35),
       (44, 8, 4, 3, 'on sen fou', 0, TRUE, '2024-06-16 10:22:00', 0, 27),

       (45, 7, 5, 5, 'trop long pas lu', 2, TRUE, '2024-06-16 10:25:00', 1, 19),
       (46, 6, 5, 6, 'fake', 1, TRUE, '2024-06-16 10:27:00', 0, 23),

       (47, 5, 6, 7, 'encore un truc de bobo', 2, TRUE, '2024-06-16 10:30:00', 1, 26),
       (48, 4, 6, 3, 'je comprends rien', 3, TRUE, '2024-06-16 10:32:00', 0, 17),

       (49, 3, 7, 1, 'zero effort lol', 1, TRUE, '2024-06-16 10:35:00', 0, 24),
       (50, 2, 7, 5, 'vous etes serieux la ?', 2, TRUE, '2024-06-16 10:37:00', 0, 20),

       (51, 1, 1, 2, 'blabla marketing', 1, TRUE, '2024-06-16 10:40:00', 0, 22),
       (52, 15, 1, 3, 'rien a dire', 2, TRUE, '2024-06-16 10:42:00', 0, 18),

       (53, 14, 3, 4, 'ok cool story', 2, TRUE, '2024-06-16 10:45:00', 0, 21),
       (54, 13, 3, 6, 'c est faux', 1, TRUE, '2024-06-16 10:47:00', 0, 23),

       (55, 12, 4, 5, 'les gens qui bossent la sont bizarres', 2, TRUE, '2024-06-16 10:50:00', 0, 29),
       (56, 11, 5, 7, 'j ai pas lu mais je suis pas d accord', 1, TRUE, '2024-06-16 10:55:00', 0, 31);

INSERT INTO comment_reaction
    (account_id, comment_id, is_upvote)
VALUES (2, 1, TRUE),
       (4, 1, TRUE),
       (5, 1, TRUE),
       (1, 2, FALSE),
       (3, 2, TRUE),
       (1, 3, TRUE),
       (5, 3, TRUE),
       (1, 4, TRUE),
       (2, 4, TRUE),
       (3, 4, TRUE),
       (5, 4, TRUE),
       (6, 4, TRUE),
       (7, 4, TRUE),
       (8, 4, TRUE),
       (9, 4, TRUE),
       (10, 4, TRUE),
       (11, 4, TRUE),
       (12, 4, FALSE),
       (13, 4, FALSE),
       (1, 5, TRUE),
       (7, 5, TRUE),
       (8, 5, FALSE),
       (2, 6, TRUE),
       (3, 6, TRUE),
       (4, 6, TRUE),
       (9, 6, TRUE),
       (10, 6, FALSE),
       (2, 7, TRUE),
       (5, 7, TRUE),
       (1, 8, TRUE),
       (2, 8, TRUE),
       (3, 8, TRUE),
       (4, 8, TRUE),
       (5, 8, TRUE);