"""
CineMatch Data Preparation Script
Creates and formats a rich, self-contained local movie dataset (data/movies.csv).
No external database required.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
OUTPUT_CSV = os.path.join(DATA_DIR, "movies.csv")

MOVIES_DATA = [
    # Sci-Fi & Mind-Bending
    {
        "id": 1,
        "title": "Inception",
        "year": 2010,
        "genres": "Action, Sci-Fi, Thriller",
        "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O., but his tragic past may doom the project and his team to disaster.",
        "keywords": "dreams, subconscious, heist, mind-bending, reality manipulation, memory, guilt",
        "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page, Tom Hardy, Ken Watanabe",
        "director": "Christopher Nolan",
        "rating": 8.8,
        "vote_count": 2400000,
        "poster_path": "https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep2P1QiDKuh.jpg"
    },
    {
        "id": 2,
        "title": "Interstellar",
        "year": 2014,
        "genres": "Adventure, Drama, Sci-Fi",
        "overview": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans across a mysterious wormhole near Saturn.",
        "keywords": "space exploration, wormhole, black hole, time dilation, father daughter, survival, love across dimensions",
        "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine, Matt Damon",
        "director": "Christopher Nolan",
        "rating": 8.7,
        "vote_count": 2000000,
        "poster_path": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
    },
    {
        "id": 3,
        "title": "The Matrix",
        "year": 1999,
        "genres": "Action, Sci-Fi",
        "overview": "When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence.",
        "keywords": "cyberpunk, simulation, artificial intelligence, chosen one, martial arts, dystopian, reality",
        "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving, Joe Pantoliano",
        "director": "Lana Wachowski, Lilly Wachowski",
        "rating": 8.7,
        "vote_count": 2000000,
        "poster_path": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
    },
    {
        "id": 4,
        "title": "Blade Runner 2049",
        "year": 2017,
        "genres": "Action, Drama, Mystery, Sci-Fi, Thriller",
        "overview": "Young Blade Runner K\'s discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard, who\'s been missing for thirty years, threatening what remains of society.",
        "keywords": "cyberpunk, replicants, existential, artificial intelligence, dystopian, loneliness, atmospheric, visual masterpiece",
        "cast": "Ryan Gosling, Harrison Ford, Ana de Armas, Sylvia Hoeks, Robin Wright",
        "director": "Denis Villeneuve",
        "rating": 8.0,
        "vote_count": 650000,
        "poster_path": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg"
    },
    {
        "id": 5,
        "title": "Arrival",
        "year": 2016,
        "genres": "Drama, Mystery, Sci-Fi",
        "overview": "Linguistics professor Louise Banks leads an elite team of investigators when gigantic spaceships touch down in 12 locations around the world. As humanity teeters on the verge of global war, Banks must learn to communicate with alien visitors.",
        "keywords": "alien contact, linguistics, non-linear time, emotional twist, grief, motherhood, world peace, thoughtful sci-fi",
        "cast": "Amy Adams, Jeremy Renner, Forest Whitaker, Michael Stuhlbarg, Tzi Ma",
        "director": "Denis Villeneuve",
        "rating": 7.9,
        "vote_count": 750000,
        "poster_path": "https://image.tmdb.org/t/p/w500/x2O0O229ITx6igAgiT6J9N8vvNk.jpg"
    },
    {
        "id": 6,
        "title": "Dune: Part Two",
        "year": 2024,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the universe, he endeavors to prevent a terrible future.",
        "keywords": "desert, prophecy, messiah, giant sandworms, space empire, revenge, epic scale, war",
        "cast": "Timothée Chalamet, Zendaya, Rebecca Ferguson, Javier Bardem, Austin Butler, Florence Pugh",
        "director": "Denis Villeneuve",
        "rating": 8.6,
        "vote_count": 480000,
        "poster_path": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg"
    },
    {
        "id": 7,
        "title": "Eternal Sunshine of the Spotless Mind",
        "year": 2004,
        "genres": "Drama, Romance, Sci-Fi",
        "overview": "When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories. As his memories vanish, he realizes he still loves her.",
        "keywords": "memory erasure, heartbreak, romantic drama, surrealism, bittersweet, human connection, psychological romance",
        "cast": "Jim Carrey, Kate Winslet, Kirsten Dunst, Mark Ruffalo, Elijah Wood",
        "director": "Michel Gondry",
        "rating": 8.3,
        "vote_count": 1100000,
        "poster_path": "https://image.tmdb.org/t/p/w500/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg"
    },
    {
        "id": 8,
        "title": "Her",
        "year": 2013,
        "genres": "Drama, Romance, Sci-Fi",
        "overview": "In a near future, a lonely writer develops an unlikely relationship with an operating system designed to meet his every need.",
        "keywords": "artificial intelligence, loneliness, modern relationships, melancholy, intimacy, futuristic, soul connection",
        "cast": "Joaquin Phoenix, Scarlett Johansson, Amy Adams, Rooney Mara, Chris Pratt",
        "director": "Spike Jonze",
        "rating": 8.0,
        "vote_count": 700000,
        "poster_path": "https://image.tmdb.org/t/p/w500/yk4J4aC059v9LtNV9Fd01fMh9ne.jpg"
    },
    {
        "id": 9,
        "title": "The Prestige",
        "year": 2006,
        "genres": "Drama, Mystery, Sci-Fi, Thriller",
        "overview": "After a tragic accident, two stage magicians in Victorian London engage in a battle to create the ultimate illusion while sacrificing everything they have to outwit each other.",
        "keywords": "magicians, rivalry, obsession, shocking twist, teleportation, Victorian era, sacrifice, revenge",
        "cast": "Christian Bale, Hugh Jackman, Scarlett Johansson, Michael Caine, David Bowie",
        "director": "Christopher Nolan",
        "rating": 8.5,
        "vote_count": 1400000,
        "poster_path": "https://image.tmdb.org/t/p/w500/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg"
    },
    {
        "id": 10,
        "title": "Ex Machina",
        "year": 2014,
        "genres": "Drama, Sci-Fi, Thriller",
        "overview": "A young programmer is selected to participate in a ground-breaking experiment in synthetic intelligence by evaluating the human qualities of a highly advanced humanoid A.I.",
        "keywords": "Turing test, artificial intelligence, manipulation, psychological tension, isolated facility, deception, android",
        "cast": "Alicia Vikander, Domhnall Gleeson, Oscar Isaac, Sonoya Mizuno",
        "director": "Alex Garland",
        "rating": 7.7,
        "vote_count": 560000,
        "poster_path": "https://image.tmdb.org/t/p/w500/btbRB7BrD88799HA9yQ9v3WzYfM.jpg"
    },
    {
        "id": 11,
        "title": "Everything Everywhere All at Once",
        "year": 2022,
        "genres": "Action, Adventure, Comedy, Sci-Fi",
        "overview": "A middle-aged Chinese immigrant is swept up into an insane adventure in which she alone can save existence by exploring other universes and connecting with the lives she could have led.",
        "keywords": "multiverse, family, mother daughter, nihilism, existentialism, absurdity, martial arts, emotional healing",
        "cast": "Michelle Yeoh, Stephanie Hsu, Ke Huy Quan, Jamie Lee Curtis, James Hong",
        "director": "Daniel Kwan, Daniel Scheinert",
        "rating": 8.1,
        "vote_count": 520000,
        "poster_path": "https://image.tmdb.org/t/p/w500/w3LxiVYPqRLexPkaekcr9vg57J7.jpg"
    },
    {
        "id": 12,
        "title": "Tenet",
        "year": 2020,
        "genres": "Action, Sci-Fi, Thriller",
        "overview": "Armed with only one word, Tenet, and fighting for the survival of the entire world, a Protagonist journeys through a twilight world of international espionage on a mission that will unfold in something beyond real time.",
        "keywords": "time inversion, espionage, mind-bending, temporal warfare, paradoxes, high concept action, blockbuster",
        "cast": "John David Washington, Robert Pattinson, Elizabeth Debicki, Kenneth Branagh",
        "director": "Christopher Nolan",
        "rating": 7.3,
        "vote_count": 580000,
        "poster_path": "https://image.tmdb.org/t/p/w500/aCIFMriQ2vtJHNxQIASIGjgOkbt.jpg"
    },

    # Dark Psychological Thrillers & Mystery
    {
        "id": 13,
        "title": "Shutter Island",
        "year": 2010,
        "genres": "Mystery, Thriller",
        "overview": "In 1954, a U.S. Marshal investigates the disappearance of a murderer who escaped from a hospital for the criminally insane on a remote island, only to discover terrifying secrets about the facility and himself.",
        "keywords": "psychiatric hospital, shocking twist, paranoia, mental health, conspiracy, hallucination, grief, guilt",
        "cast": "Leonardo DiCaprio, Mark Ruffalo, Ben Kingsley, Michelle Williams, Max von Sydow",
        "director": "Martin Scorsese",
        "rating": 8.2,
        "vote_count": 1450000,
        "poster_path": "https://image.tmdb.org/t/p/w500/kve20tXwUZpu4GUX8l6X7Z4QIIL.jpg"
    },
    {
        "id": 14,
        "title": "Fight Club",
        "year": 1999,
        "genres": "Action, Drama, Thriller",
        "overview": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more, challenging corporate conformity and male identity.",
        "keywords": "insomnia, alter ego, underground fight club, anti-consumerism, shocking twist, psychological breakdown, cult classic",
        "cast": "Brad Pitt, Edward Norton, Helena Bonham Carter, Meat Loaf, Jared Leto",
        "director": "David Fincher",
        "rating": 8.8,
        "vote_count": 2300000,
        "poster_path": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"
    },
    {
        "id": 15,
        "title": "Se7en",
        "year": 1995,
        "genres": "Crime, Drama, Mystery, Thriller",
        "overview": "Two detectives, a rookie and a veteran, hunt a serial killer who uses the seven deadly sins as his motives in a perpetually rain-soaked, morally bankrupt metropolis.",
        "keywords": "serial killer, seven deadly sins, dark noir, shocking ending, detectives, moral decay, psychological horror",
        "cast": "Morgan Freeman, Brad Pitt, Kevin Spacey, Gwyneth Paltrow, John C. McGinley",
        "director": "David Fincher",
        "rating": 8.6,
        "vote_count": 1800000,
        "poster_path": "https://image.tmdb.org/t/p/w500/6yoghtyTBoPmuZzhi0PuhPnWqPt.jpg"
    },
    {
        "id": 16,
        "title": "The Silence of the Lambs",
        "year": 1991,
        "genres": "Crime, Drama, Thriller",
        "overview": "A young F.B.I. cadet must receive the help of an incarcerated and manipulative cannibal killer to help catch another serial killer, a madman who skins his victims.",
        "keywords": "Hannibal Lecter, FBI, psychological game, serial killer, cannibal, suspense, mind games, iconic villain",
        "cast": "Jodie Foster, Anthony Hopkins, Scott Glenn, Ted Levine, Anthony Heald",
        "director": "Jonathan Demme",
        "rating": 8.6,
        "vote_count": 1500000,
        "poster_path": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg"
    },
    {
        "id": 17,
        "title": "Parasite",
        "year": 2019,
        "genres": "Drama, Thriller",
        "overview": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan in Seoul.",
        "keywords": "class struggle, social satire, dark comedy, home invasion, shocking twists, wealth inequality, suspense",
        "cast": "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong, Choi Woo-shik, Park So-dam",
        "director": "Bong Joon Ho",
        "rating": 8.5,
        "vote_count": 920000,
        "poster_path": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"
    },
    {
        "id": 18,
        "title": "Gone Girl",
        "year": 2014,
        "genres": "Drama, Mystery, Thriller",
        "overview": "With his wife\'s disappearance having become the focus of an intense media circus, a man sees the spotlight turned on him when it\'s suspected that he may not be innocent.",
        "keywords": "toxic marriage, psychopathic deception, media frenzy, framing, unreliable narrator, shocking twist, dark satire",
        "cast": "Ben Affleck, Rosamund Pike, Neil Patrick Harris, Tyler Perry, Carrie Coon",
        "director": "David Fincher",
        "rating": 8.1,
        "vote_count": 1050000,
        "poster_path": "https://image.tmdb.org/t/p/w500/qymaJhucquUwjpb8DYBPynqTk5L.jpg"
    },
    {
        "id": 19,
        "title": "Prisoners",
        "year": 2013,
        "genres": "Crime, Drama, Mystery, Thriller",
        "overview": "When Keller Dover\'s daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads and the pressure mounts.",
        "keywords": "abduction, vigilante justice, morality, detective, bleak atmosphere, intense suspense, parental desperation",
        "cast": "Hugh Jackman, Jake Gyllenhaal, Viola Davis, Maria Bello, Paul Dano",
        "director": "Denis Villeneuve",
        "rating": 8.1,
        "vote_count": 780000,
        "poster_path": "https://image.tmdb.org/t/p/w500/tuZhZ6biFMr5n9Y2hX0yE0F1E2K.jpg"
    },
    {
        "id": 20,
        "title": "Zodiac",
        "year": 2007,
        "genres": "Crime, Drama, History, Mystery, Thriller",
        "overview": "Between 1968 and 1983, a San Francisco cartoonist becomes an amateur detective obsessed with tracking down the Zodiac Killer, an unidentified murderer who terrorizes northern California with cryptograms.",
        "keywords": "unsolved mystery, obsession, serial killer, journalism, cipher, 1970s, police investigation, tension",
        "cast": "Jake Gyllenhaal, Mark Ruffalo, Robert Downey Jr., Anthony Edwards, Brian Cox",
        "director": "David Fincher",
        "rating": 7.7,
        "vote_count": 620000,
        "poster_path": "https://image.tmdb.org/t/p/w500/6iyTf9E6zP45V1zH1W9s6t9yC1G.jpg"
    },
    {
        "id": 21,
        "title": "Memento",
        "year": 2000,
        "genres": "Mystery, Thriller",
        "overview": "A man with short-term memory loss attempts to track down his wife\'s murderer using a complex system of Polaroid photographs and tattoos.",
        "keywords": "anterograde amnesia, reverse chronology, shocking twist, revenge, unreliable narrator, deception, psychological",
        "cast": "Guy Pearce, Carrie-Anne Moss, Joe Pantoliano, Mark Boone Junior",
        "director": "Christopher Nolan",
        "rating": 8.4,
        "vote_count": 1300000,
        "poster_path": "https://image.tmdb.org/t/p/w500/yuNs09hvpHVU1cBTCAk9z9Sp2D.jpg"
    },
    {
        "id": 22,
        "title": "Nightcrawler",
        "year": 2014,
        "genres": "Crime, Drama, Thriller",
        "overview": "When Louis Bloom, a con man desperate for work, muscles into the world of L.A. crime journalism, he blurs the line between observer and participant to become the star of his own story.",
        "keywords": "sociopath, freelance journalism, nocturnal LA, moral decay, obsession, sensationalism, dark ambition",
        "cast": "Jake Gyllenhaal, Rene Russo, Bill Paxton, Riz Ahmed",
        "director": "Dan Gilroy",
        "rating": 7.8,
        "vote_count": 580000,
        "poster_path": "https://image.tmdb.org/t/p/w500/8A7U4mF17uT7xM0zN1V3yM9pP8x.jpg"
    },
    {
        "id": 23,
        "title": "Get Out",
        "year": 2017,
        "genres": "Horror, Mystery, Thriller",
        "overview": "A young African-American visits his white girlfriend\'s parents for the weekend, where his simmering uneasiness about their reception of him eventually reaches a boiling point.",
        "keywords": "social horror, psychological thriller, hypnotism, conspiracy, racism, shocking twist, suspense",
        "cast": "Daniel Kaluuya, Allison Williams, Bradley Whitford, Catherine Keener, Lil Rel Howery",
        "director": "Jordan Peele",
        "rating": 7.8,
        "vote_count": 680000,
        "poster_path": "https://image.tmdb.org/t/p/w500/tFXcEccSQMf3lfhfXKSU9iRBpa3.jpg"
    },
    {
        "id": 24,
        "title": "Hereditary",
        "year": 2018,
        "genres": "Drama, Horror, Mystery, Thriller",
        "overview": "A grieving family is haunted by tragic and disturbing occurrences after the death of their secretive grandmother.",
        "keywords": "grief, demonic cult, family trauma, disturbing horror, occult, psychological breakdown, terrifying",
        "cast": "Toni Collette, Alex Wolff, Milly Shapiro, Gabriel Byrne, Ann Dowd",
        "director": "Ari Aster",
        "rating": 7.3,
        "vote_count": 420000,
        "poster_path": "https://image.tmdb.org/t/p/w500/p9fmuz2Oj3o4U04cM13iQz7k8bW.jpg"
    },

    # Action, Crime & Epic
    {
        "id": 25,
        "title": "The Dark Knight",
        "year": 2008,
        "genres": "Action, Crime, Drama, Thriller",
        "overview": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "keywords": "Joker, chaos vs order, moral dilemmas, vigilante, crime epic, high stakes, masterclass acting, superhero",
        "cast": "Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine, Maggie Gyllenhaal, Gary Oldman, Morgan Freeman",
        "director": "Christopher Nolan",
        "rating": 9.0,
        "vote_count": 2900000,
        "poster_path": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
    },
    {
        "id": 26,
        "title": "The Godfather",
        "year": 1972,
        "genres": "Crime, Drama",
        "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant youngest son.",
        "keywords": "mafia, family loyalty, power corruption, Italian-American, organized crime, moral descent, cinema classic",
        "cast": "Marlon Brando, Al Pacino, James Caan, Robert Duvall, Diane Keaton",
        "director": "Francis Ford Coppola",
        "rating": 9.2,
        "vote_count": 2000000,
        "poster_path": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"
    },
    {
        "id": 27,
        "title": "Pulp Fiction",
        "year": 1994,
        "genres": "Crime, Drama",
        "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "keywords": "non-linear storytelling, witty dialogue, hitmen, pop culture, organized crime, dark comedy, iconic soundtrack",
        "cast": "John Travolta, Samuel L. Jackson, Uma Thurman, Bruce Willis, Ving Rhames",
        "director": "Quentin Tarantino",
        "rating": 8.9,
        "vote_count": 2200000,
        "poster_path": "https://image.tmdb.org/t/p/w500/d5iIlFnGhFvl09Y77bK75T09xsm.jpg"
    },
    {
        "id": 28,
        "title": "Goodfellas",
        "year": 1990,
        "genres": "Biography, Crime, Drama",
        "overview": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito in the Italian-American crime syndicate.",
        "keywords": "mobsters, Brooklyn mafia, rise and fall, cocaine, heist, fast-paced, based on true story, voiceover",
        "cast": "Robert De Niro, Ray Liotta, Joe Pesci, Lorraine Bracco, Paul Sorvino",
        "director": "Martin Scorsese",
        "rating": 8.7,
        "vote_count": 1300000,
        "poster_path": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZZ79RuvX7hIe.jpg"
    },
    {
        "id": 29,
        "title": "Mad Max: Fury Road",
        "year": 2015,
        "genres": "Action, Adventure, Sci-Fi",
        "overview": "In a post-apocalyptic wasteland, a woman rebels against a tyrannical ruler in search for her homeland with the aid of a group of female prisoners, a psychotic worshiper, and a drifter named Max.",
        "keywords": "post-apocalypse, relentless vehicular chase, feminist rebellion, desert wasteland, practical stunts, octane adrenaline",
        "cast": "Tom Hardy, Charlize Theron, Nicholas Hoult, Hugh Keays-Byrne, Zoe Kravitz",
        "director": "George Miller",
        "rating": 8.1,
        "vote_count": 1100000,
        "poster_path": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg"
    },
    {
        "id": 30,
        "title": "Gladiator",
        "year": 2000,
        "genres": "Action, Adventure, Drama",
        "overview": "A former Roman General sets out to exact vengeance against the corrupt emperor who murdered his family and sent him into slavery.",
        "keywords": "ancient Rome, colosseum, vengeance, honor, sword fighting, epic spectacle, tragic hero",
        "cast": "Russell Crowe, Joaquin Phoenix, Connie Nielsen, Oliver Reed, Richard Harris",
        "director": "Ridley Scott",
        "rating": 8.5,
        "vote_count": 1600000,
        "poster_path": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg"
    },
    {
        "id": 31,
        "title": "Oppenheimer",
        "year": 2023,
        "genres": "Biography, Drama, History",
        "overview": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during the Manhattan Project.",
        "keywords": "atomic bomb, nuclear physics, moral guilt, McCarthyism, political betrayal, historical drama, intense score",
        "cast": "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr., Florence Pugh",
        "director": "Christopher Nolan",
        "rating": 8.9,
        "vote_count": 820000,
        "poster_path": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg"
    },
    {
        "id": 32,
        "title": "Django Unchained",
        "year": 2012,
        "genres": "Drama, Western",
        "overview": "With the help of a German bounty hunter, a freed slave sets out to rescue his wife from a brutal Mississippi plantation owner.",
        "keywords": "bounty hunter, antebellum South, revenge, explosive violence, stylized Western, witty dialogue",
        "cast": "Jamie Foxx, Christoph Waltz, Leonardo DiCaprio, Kerry Washington, Samuel L. Jackson",
        "director": "Quentin Tarantino",
        "rating": 8.5,
        "vote_count": 1700000,
        "poster_path": "https://image.tmdb.org/t/p/w500/7oWY8vdWW7thTzEN3Y9P9hgqQ37.jpg"
    },

    # Heartwarming, Comedy, Friends & Romance
    {
        "id": 33,
        "title": "Superbad",
        "year": 2007,
        "genres": "Comedy",
        "overview": "Two co-dependent high school seniors are forced to deal with separation anxiety after their plan to stage a booze-soaked party goes awry.",
        "keywords": "high school, best friends, funny party, coming of age, McLovin, fake ID, friendship comedy",
        "cast": "Jonah Hill, Michael Cera, Christopher Mintz-Plasse, Bill Hader, Seth Rogen, Emma Stone",
        "director": "Greg Mottola",
        "rating": 7.6,
        "vote_count": 650000,
        "poster_path": "https://image.tmdb.org/t/p/w500/ek8e8txUyUv18qBuGhmc59Nd1bs.jpg"
    },
    {
        "id": 34,
        "title": "The Grand Budapest Hotel",
        "year": 2014,
        "genres": "Adventure, Comedy, Crime",
        "overview": "A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy in the hotel\'s glorious years under an exceptional concierge.",
        "keywords": "whimsical, symmetrical visuals, concierge, stolen painting, quirky humor, friendship, pastel aesthetic",
        "cast": "Ralph Fiennes, F. Murray Abraham, Mathieu Amalric, Adrien Brody, Willem Dafoe, Saoirse Ronan",
        "director": "Wes Anderson",
        "rating": 8.1,
        "vote_count": 920000,
        "poster_path": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg"
    },
    {
        "id": 35,
        "title": "La La Land",
        "year": 2016,
        "genres": "Comedy, Drama, Music, Romance",
        "overview": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.",
        "keywords": "jazz, Hollywood dreams, bittersweet romance, musical numbers, nostalgia, ambition vs love, stunning cinematography",
        "cast": "Ryan Gosling, Emma Stone, John Legend, Rosemarie DeWitt, J.K. Simmons",
        "director": "Damien Chazelle",
        "rating": 8.0,
        "vote_count": 680000,
        "poster_path": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkVJt0Rf0.jpg"
    },
    {
        "id": 36,
        "title": "The Hangover",
        "year": 2009,
        "genres": "Comedy",
        "overview": "Three buddies wake up from a bachelor party in Las Vegas, with no memory of the previous night and the bachelor missing. They make their way around the city in order to find their friend before his wedding.",
        "keywords": "bachelor party, Las Vegas, memory loss, crazy mystery, tiger in bathroom, hilarious buddy adventure",
        "cast": "Bradley Cooper, Ed Helms, Zach Galifianakis, Justin Bartha, Ken Jeong",
        "director": "Todd Phillips",
        "rating": 7.7,
        "vote_count": 850000,
        "poster_path": "https://image.tmdb.org/t/p/w500/ulHQB0rC1wG6VqP4w7v5vF4F4YQ.jpg"
    },
    {
        "id": 37,
        "title": "500 Days of Summer",
        "year": 2009,
        "genres": "Comedy, Drama, Romance",
        "overview": "An offbeat romantic comedy about a woman who doesn\'t believe true love exists, and the young man who falls for her.",
        "keywords": "non-linear romance, heartbreak, realistic love, indie soundtrack, expectation vs reality, growth",
        "cast": "Joseph Gordon-Levitt, Zooey Deschanel, Geoffrey Arend, Chloe Grace Moretz",
        "director": "Marc Webb",
        "rating": 7.7,
        "vote_count": 550000,
        "poster_path": "https://image.tmdb.org/t/p/w500/f9mbM0Y6RwxPp4BhBg3OPg09Y6.jpg"
    },
    {
        "id": 38,
        "title": "Before Sunrise",
        "year": 1995,
        "genres": "Drama, Romance",
        "overview": "A young man and woman meet on a train in Europe, and wind up spending one evening together in Vienna. Unfortunately, both know that this will probably be their only night together.",
        "keywords": "Vienna, deep conversation, fleeting romance, connection, philosophical dialogue, romantic walk",
        "cast": "Ethan Hawke, Julie Delpy, Andrea Eckert, Hanno Pöschl",
        "director": "Richard Linklater",
        "rating": 8.1,
        "vote_count": 350000,
        "poster_path": "https://image.tmdb.org/t/p/w500/kf1Jb14a8Y4y3F5R9q7hG0h3C9.jpg"
    },
    {
        "id": 39,
        "title": "About Time",
        "year": 2013,
        "genres": "Comedy, Drama, Fantasy, Romance, Sci-Fi",
        "overview": "At the age of 21, Tim discovers he can travel in time and change what happens and has happened in his own life. His decision to make his world a better place by getting a girlfriend turns out not to be as easy as you might think.",
        "keywords": "time travel, father son relationship, tearjerker, appreciate life, warm romance, heartwarming, British humor",
        "cast": "Domhnall Gleeson, Rachel McAdams, Bill Nighy, Lydia Wilson, Margot Robbie",
        "director": "Richard Curtis",
        "rating": 7.8,
        "vote_count": 420000,
        "poster_path": "https://image.tmdb.org/t/p/w500/q2iV5PZ9f1X8a7y9Q9M6N8L9q7.jpg"
    },
    {
        "id": 40,
        "title": "Whiplash",
        "year": 2014,
        "genres": "Drama, Music",
        "overview": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student\'s potential.",
        "keywords": "jazz drumming, abusive mentor, perfectionism, intense psychological battle, blood sweat tears, electric climax",
        "cast": "Miles Teller, J.K. Simmons, Paul Reiser, Melissa Benoist, Austin Stowell",
        "director": "Damien Chazelle",
        "rating": 8.5,
        "vote_count": 1000000,
        "poster_path": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg"
    },

    # Animation, Anime & Fantasy
    {
        "id": 41,
        "title": "Spirited Away",
        "year": 2001,
        "genres": "Adventure, Animation, Family, Fantasy",
        "overview": "During her family\'s move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.",
        "keywords": "Studio Ghibli, spirit bathhouse, Japanese folklore, coming of age, magic, nostalgic wonder, masterpiece",
        "cast": "Rumi Hiiragi, Miyu Irino, Mari Natsuki, Takashi Naito, Yasuko Sawaguchi",
        "director": "Hayao Miyazaki",
        "rating": 8.6,
        "vote_count": 850000,
        "poster_path": "https://image.tmdb.org/t/p/w500/393rA7P0qDzoE97WsNn16Vv4vP.jpg"
    },
    {
        "id": 42,
        "title": "Your Name",
        "year": 2016,
        "genres": "Animation, Drama, Fantasy, Romance",
        "overview": "Two strangers find themselves linked in a bizarre way. When a connection forms, will distance be the only thing to keep them apart?",
        "keywords": "body swapping, comet catastrophe, time slip, emotional yearning, fate, stunning anime visuals, soundtrack",
        "cast": "Ryunosuke Kamiki, Mone Kamishiraishi, Ryo Narita, Aoi Yuki",
        "director": "Makoto Shinkai",
        "rating": 8.4,
        "vote_count": 320000,
        "poster_path": "https://image.tmdb.org/t/p/w500/q719qXXEzOoYaps6XZawPWhNUm7.jpg"
    },
    {
        "id": 43,
        "title": "Spider-Man: Into the Spider-Verse",
        "year": 2018,
        "genres": "Action, Adventure, Animation, Sci-Fi",
        "overview": "Teen Miles Morales becomes the new Spider-Man and must join with five spider-powered individuals from other dimensions to stop a threat for all realities.",
        "keywords": "multiverse, comic book visual style, hip hop soundtrack, father son, leap of faith, coming of age, superheroes",
        "cast": "Shameik Moore, Jake Johnson, Hailee Steinfeld, Mahershala Ali, Nicolas Cage",
        "director": "Bob Persichetti, Peter Ramsey, Rodney Rothman",
        "rating": 8.4,
        "vote_count": 680000,
        "poster_path": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg"
    },
    {
        "id": 44,
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "year": 2001,
        "genres": "Action, Adventure, Drama, Fantasy",
        "overview": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.",
        "keywords": "Middle-earth, fellowship, One Ring, wizards, elves, dwarves, epic fantasy quest, friendship",
        "cast": "Elijah Wood, Ian McKellen, Viggo Mortensen, Sean Astin, Orlando Bloom",
        "director": "Peter Jackson",
        "rating": 8.9,
        "vote_count": 2000000,
        "poster_path": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cDK6.jpg"
    },
    {
        "id": 45,
        "title": "The Shawshank Redemption",
        "year": 1994,
        "genres": "Drama",
        "overview": "Over the course of several years, two convicts form a friendship, seeking consolation and, eventually, redemption through basic compassion.",
        "keywords": "prison escape, friendship, hope, wrongful conviction, corruption, resilience, timeless masterpiece",
        "cast": "Tim Robbins, Morgan Freeman, Bob Gunton, William Sadler, Clancy Brown",
        "director": "Frank Darabont",
        "rating": 9.3,
        "vote_count": 2900000,
        "poster_path": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
    }
]

def build_combined_text(row):
    """
    Constructs an information-dense combined metadata string for embedding generation.
    Handles missing/null fields cleanly.
    """
    title = str(row.get("title", "")).strip()
    genres = str(row.get("genres", "")).replace(",", " ").strip()
    overview = str(row.get("overview", "")).strip()
    keywords = str(row.get("keywords", "")).strip()
    cast = str(row.get("cast", "")).strip()
    director = str(row.get("director", "")).strip()

    parts = []
    if title:
        parts.append(f"{title}.")
    if genres:
        parts.append(f"Genres: {genres}.")
    if overview:
        parts.append(f"Overview: {overview}")
    if keywords:
        parts.append(f"Themes and keywords: {keywords}.")
    if cast:
        parts.append(f"Starring: {cast}.")
    if director:
        parts.append(f"Directed by {director}.")

    return " ".join(parts)

def main():
    df = pd.DataFrame(MOVIES_DATA)
    df["combined_text"] = df.apply(build_combined_text, axis=1)
    
    # Save CSV
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"[SUCCESS] Saved {len(df)} movies to {OUTPUT_CSV}")
    print("Sample combined_text:")
    print(df["combined_text"].iloc[0][:250] + "...")

if __name__ == "__main__":
    main()
