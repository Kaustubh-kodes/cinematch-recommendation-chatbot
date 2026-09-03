export interface BookItem {
  book_id: number;
  title: string;
  authors: string;
  genres: string;
  rating: number;
}

export const MOCK_BOOKS: BookItem[] = [
  // Sci-Fi & Dystopian
  { book_id: 1, title: "Dune", authors: "Frank Herbert", genres: "Sci-Fi|Adventure|Classics", rating: 4.9 },
  { book_id: 2, title: "Neuromancer", authors: "William Gibson", genres: "Sci-Fi|Cyberpunk", rating: 4.6 },
  { book_id: 3, title: "Snow Crash", authors: "Neal Stephenson", genres: "Sci-Fi|Cyberpunk", rating: 4.5 },
  { book_id: 4, title: "The Three-Body Problem", authors: "Cixin Liu", genres: "Sci-Fi|Mystery", rating: 4.8 },
  { book_id: 5, title: "Project Hail Mary", authors: "Andy Weir", genres: "Sci-Fi|Adventure", rating: 4.9 },
  { book_id: 6, title: "The Martian", authors: "Andy Weir", genres: "Sci-Fi|Adventure", rating: 4.8 },
  { book_id: 7, title: "Ender's Game", authors: "Orson Scott Card", genres: "Sci-Fi|Adventure", rating: 4.7 },
  { book_id: 8, title: "Foundation", authors: "Isaac Asimov", genres: "Sci-Fi|Classics", rating: 4.8 },
  { book_id: 9, title: "Hyperion", authors: "Dan Simmons", genres: "Sci-Fi|Fantasy", rating: 4.7 },
  { book_id: 10, title: "1984", authors: "George Orwell", genres: "Classics|Dystopian|Sci-Fi", rating: 4.9 },
  { book_id: 11, title: "Brave New World", authors: "Aldous Huxley", genres: "Classics|Dystopian|Sci-Fi", rating: 4.7 },
  { book_id: 12, title: "Fahrenheit 451", authors: "Ray Bradbury", genres: "Classics|Dystopian|Sci-Fi", rating: 4.6 },
  { book_id: 13, title: "The Hunger Games", authors: "Suzanne Collins", genres: "Adventure|Dystopian|Sci-Fi", rating: 4.7 },
  { book_id: 14, title: "Do Androids Dream of Electric Sheep?", authors: "Philip K. Dick", genres: "Sci-Fi|Classics", rating: 4.6 },
  { book_id: 15, title: "Children of Time", authors: "Adrian Tchaikovsky", genres: "Sci-Fi|Space", rating: 4.7 },

  // Fantasy & Adventure
  { book_id: 16, title: "The Hobbit", authors: "J.R.R. Tolkien", genres: "Fantasy|Adventure|Classics", rating: 4.8 },
  { book_id: 17, title: "The Fellowship of the Ring", authors: "J.R.R. Tolkien", genres: "Fantasy|Adventure|Classics", rating: 4.9 },
  { book_id: 18, title: "A Game of Thrones", authors: "George R.R. Martin", genres: "Fantasy|Drama", rating: 4.8 },
  { book_id: 19, title: "The Name of the Wind", authors: "Patrick Rothfuss", genres: "Fantasy|Adventure", rating: 4.8 },
  { book_id: 20, title: "The Way of Kings", authors: "Brandon Sanderson", genres: "Fantasy|Epic", rating: 4.9 },
  { book_id: 21, title: "Mistborn: The Final Empire", authors: "Brandon Sanderson", genres: "Fantasy|Action", rating: 4.8 },
  { book_id: 22, title: "Harry Potter and the Sorcerer's Stone", authors: "J.K. Rowling", genres: "Fantasy|Classics", rating: 4.8 },
  { book_id: 23, title: "The Lies of Locke Lamora", authors: "Scott Lynch", genres: "Fantasy|Crime", rating: 4.7 },
  { book_id: 24, title: "The Blade Itself", authors: "Joe Abercrombie", genres: "Fantasy|Grimdark", rating: 4.6 },
  { book_id: 25, title: "The Priory of the Orange Tree", authors: "Samantha Shannon", genres: "Fantasy|Epic", rating: 4.5 },

  // Thriller & Mystery
  { book_id: 26, title: "The Da Vinci Code", authors: "Dan Brown", genres: "Mystery|Thriller", rating: 4.5 },
  { book_id: 27, title: "Angels & Demons", authors: "Dan Brown", genres: "Mystery|Thriller", rating: 4.6 },
  { book_id: 28, title: "Gone Girl", authors: "Gillian Flynn", genres: "Mystery|Thriller|Drama", rating: 4.7 },
  { book_id: 29, title: "The Girl with the Dragon Tattoo", authors: "Stieg Larsson", genres: "Mystery|Crime|Thriller", rating: 4.7 },
  { book_id: 30, title: "And Then There Were None", authors: "Agatha Christie", genres: "Classics|Mystery|Thriller", rating: 4.9 },
  { book_id: 31, title: "The Silent Patient", authors: "Alex Michaelides", genres: "Mystery|Psychological|Thriller", rating: 4.6 },
  { book_id: 32, title: "Shutter Island", authors: "Dennis Lehane", genres: "Mystery|Thriller", rating: 4.7 },
  { book_id: 33, title: "Big Little Lies", authors: "Liane Moriarty", genres: "Mystery|Drama", rating: 4.5 },

  // Classics, Literature & Non-Fiction
  { book_id: 34, title: "To Kill a Mockingbird", authors: "Harper Lee", genres: "Classics|Drama", rating: 4.9 },
  { book_id: 35, title: "The Great Gatsby", authors: "F. Scott Fitzgerald", genres: "Classics|Drama", rating: 4.6 },
  { book_id: 36, title: "Pride and Prejudice", authors: "Jane Austen", genres: "Romance|Classics", rating: 4.8 },
  { book_id: 37, title: "Crime and Punishment", authors: "Fyodor Dostoevsky", genres: "Classics|Psychological|Drama", rating: 4.8 },
  { book_id: 38, title: "The Catcher in the Rye", authors: "J.D. Salinger", genres: "Classics|Drama", rating: 4.4 },
  { book_id: 39, title: "The Picture of Dorian Gray", authors: "Oscar Wilde", genres: "Classics|Horror|Drama", rating: 4.7 },
  { book_id: 40, title: "The Alchemist", authors: "Paulo Coelho", genres: "Classics|Philosophy|Adventure", rating: 4.6 },
  { book_id: 41, title: "Sapiens: A Brief History of Humankind", authors: "Yuval Noah Harari", genres: "Non-Fiction|History|Philosophy", rating: 4.8 },
  { book_id: 42, title: "Atomic Habits", authors: "James Clear", genres: "Non-Fiction|Self-Help", rating: 4.9 },
  { book_id: 43, title: "Meditations", authors: "Marcus Aurelius", genres: "Classics|Philosophy", rating: 4.8 }
];
