"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Film, Sparkles, Search, Star, MessageSquare, Send, Info, Bookmark, User, 
  RefreshCw, AlertCircle, Check, X, Flame, Key, SlidersHorizontal, ArrowRight,
  ExternalLink, Layers, Play, Clock, Heart, Filter, ChevronRight, LogIn, LogOut,
  UserCircle, Settings, Shield
} from "lucide-react";
import { MOCK_MOVIES } from "@/data/movies";

interface MovieRecommendation {
  rank: number;
  id: number;
  title: string;
  year: number;
  genres: string[];
  overview: string;
  rating: number;
  vote_count?: number;
  director?: string;
  cast?: string;
  poster_path?: string;
  similarity_score: number;
  final_score?: number;
  match_reason: string;
}

interface UserProfile {
  name: string;
  email: string;
  avatar: string;
  preferredGenres: string[];
  isLoggedIn: boolean;
}

const EXAMPLE_CHIPS = [
  "Mind-bending sci-fi",
  "Dark psychological thriller with a shocking ending",
  "Funny feel-good movie to watch with friends",
  "Emotional and heartbreaking movie about loneliness and relationships",
  "Something like Interstellar but more emotional and less focused on science",
  "High stakes crime heist with intense suspense"
];

const LOCAL_POSTER_MAP: Record<string, string> = {
  "Inception": "https://image.tmdb.org/t/p/w500/ljsZTbVsrQSqZgWeep2P1QiDKuh.jpg",
  "Interstellar": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
  "The Matrix": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
  "Blade Runner 2049": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
  "Arrival": "https://image.tmdb.org/t/p/w500/x2O0O229ITx6igAgiT6J9N8vvNk.jpg",
  "Dune: Part Two": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
  "Eternal Sunshine of the Spotless Mind": "https://image.tmdb.org/t/p/w500/5MwkWH9tYHv3mV9OdYTMR5qreIz.jpg",
  "Her": "https://image.tmdb.org/t/p/w500/yk4J4aC059v9LtNV9Fd01fMh9ne.jpg",
  "The Prestige": "https://image.tmdb.org/t/p/w500/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg",
  "Ex Machina": "https://image.tmdb.org/t/p/w500/btbRB7BrD88799HA9yQ9v3WzYfM.jpg",
  "Everything Everywhere All at Once": "https://image.tmdb.org/t/p/w500/w3LxiVYPqRLexPkaekcr9vg57J7.jpg",
  "Tenet": "https://image.tmdb.org/t/p/w500/aCIFMriQ2vtJHNxQIASIGjgOkbt.jpg",
  "Shutter Island": "https://image.tmdb.org/t/p/w500/kve20tXwUZpu4GUX8l6X7Z4QIIL.jpg",
  "Fight Club": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
  "Se7en": "https://image.tmdb.org/t/p/w500/6yoghtyTBoPmuZzhi0PuhPnWqPt.jpg",
  "The Silence of the Lambs": "https://image.tmdb.org/t/p/w500/uS9m8OBk1A8eM9I042bx8XXpqAq.jpg",
  "Parasite": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
  "Gone Girl": "https://image.tmdb.org/t/p/w500/qymaJhucquUwjpb8DYBPynqTk5L.jpg",
  "Prisoners": "https://image.tmdb.org/t/p/w500/tuZhZ6biFMr5n9Y2hX0yE0F1E2K.jpg",
  "The Dark Knight": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
  "The Godfather": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
  "Pulp Fiction": "https://image.tmdb.org/t/p/w500/d5iIlFnGhFvl09Y77bK75T09xsm.jpg",
  "Goodfellas": "https://image.tmdb.org/t/p/w500/aKuFiU82s5ISJpGZZ79RuvX7hIe.jpg",
  "Mad Max: Fury Road": "https://image.tmdb.org/t/p/w500/8tZYtuWezp8JbcsvHYO0O46tFbo.jpg",
  "Gladiator": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
  "Oppenheimer": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
  "Django Unchained": "https://image.tmdb.org/t/p/w500/7oWY8vdWW7thTzEN3Y9P9hgqQ37.jpg",
  "Superbad": "https://image.tmdb.org/t/p/w500/ek8e8txUyUv18qBuGhmc59Nd1bs.jpg",
  "The Grand Budapest Hotel": "https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg",
  "La La Land": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkVJt0Rf0.jpg",
  "Whiplash": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
  "Spirited Away": "https://image.tmdb.org/t/p/w500/393rA7P0qDzoE97WsNn16Vv4vP.jpg",
  "Your Name": "https://image.tmdb.org/t/p/w500/q719qXXEzOoYaps6XZawPWhNUm7.jpg",
  "Spider-Man: Into the Spider-Verse": "https://image.tmdb.org/t/p/w500/iiZZdoQBEYBv6id8su7ImL0oCbD.jpg",
  "The Shawshank Redemption": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
};

export default function Home() {
  const [searchPrompt, setSearchPrompt] = useState("");
  const [recommendations, setRecommendations] = useState<MovieRecommendation[]>([]);
  const [enhancedQuery, setEnhancedQuery] = useState<string>("");
  
  // Loading & Modals
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState<"intent" | "embedding" | "ranking">("intent");
  const [selectedMovie, setSelectedMovie] = useState<MovieRecommendation | null>(null);
  const [showProfileModal, setShowProfileModal] = useState<boolean>(false);
  const [showWatchlistModal, setShowWatchlistModal] = useState<boolean>(false);
  const [watchlist, setWatchlist] = useState<number[]>([]);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // User Authentication / Profile State
  const [user, setUser] = useState<UserProfile>({
    name: "Kaustubh Tiwari",
    email: "kaustubh@example.com",
    avatar: "https://avatars.githubusercontent.com/u/142834906?v=4",
    preferredGenres: ["Sci-Fi", "Psychological Thriller", "Drama"],
    isLoggedIn: false
  });
  const [loginEmail, setLoginEmail] = useState("");
  const [loginName, setLoginName] = useState("");

  // Filters
  const [minRating, setMinRating] = useState<number>(0.0);
  const [selectedGenre, setSelectedGenre] = useState<string>("All");
  const [sortBy, setSortBy] = useState<"similarity" | "rating" | "year">("similarity");

  const resultsRef = useRef<HTMLDivElement>(null);

  // Load user session from localStorage
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedUser = localStorage.getItem("cinematch_user");
      if (savedUser) {
        try {
          setUser(JSON.parse(savedUser));
        } catch (e) {}
      }
      const savedWatchlist = localStorage.getItem("cinematch_watchlist");
      if (savedWatchlist) {
        try {
          setWatchlist(JSON.parse(savedWatchlist));
        } catch (e) {}
      }
    }
  }, []);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Perform Initial Default Recommendation
  useEffect(() => {
    handleSearch("Mind-bending sci-fi with emotional themes and space exploration");
  }, []);

  const handleSearch = async (queryText?: string) => {
    const prompt = (queryText || searchPrompt).trim();
    if (!prompt) return;

    setIsLoading(true);
    setLoadingStep("intent");
    setEnhancedQuery("");

    try {
      setTimeout(() => setLoadingStep("embedding"), 350);

      // Attempt FastAPI call first
      let apiSuccess = false;
      try {
        const res = await fetch("http://localhost:8000/recommend", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt, limit: 12 }),
        });

        if (res.ok) {
          const data = await res.json();
          if (data.success && data.recommendations) {
            setRecommendations(data.recommendations);
            setEnhancedQuery(data.enhanced_query || prompt);
            apiSuccess = true;
          }
        }
      } catch (err) {
        // FastAPI offline; fallback to local semantic match
      }

      // Resilient Local Semantic ML Match
      if (!apiSuccess) {
        setTimeout(() => setLoadingStep("ranking"), 700);

        setTimeout(() => {
          const pLower = prompt.toLowerCase();
          
          const scored = MOCK_MOVIES.map((movie) => {
            const mText = `${movie.title} ${movie.genres.replace(/\|/g, " ")}`.toLowerCase();
            const genreList = movie.genres.split("|");
            
            let simScore = 0.45;
            const keywords = pLower.split(/\s+/).filter(w => w.length > 3);
            let matchedKw = 0;
            keywords.forEach(kw => {
              if (mText.includes(kw)) matchedKw++;
            });
            simScore += Math.min(0.40, matchedKw * 0.15);

            if (pLower.includes("sci-fi") && movie.genres.includes("Sci-Fi")) simScore += 0.25;
            if (pLower.includes("thrill") && movie.genres.includes("Thriller")) simScore += 0.25;
            if (pLower.includes("drama") && movie.genres.includes("Drama")) simScore += 0.15;
            if (pLower.includes("action") && movie.genres.includes("Action")) simScore += 0.20;
            if (pLower.includes("comedy") && movie.genres.includes("Comedy")) simScore += 0.30;
            if (pLower.includes("horror") && movie.genres.includes("Horror")) simScore += 0.30;
            if (pLower.includes("romance") && movie.genres.includes("Romance")) simScore += 0.25;
            if (pLower.includes("interstellar") && movie.title.includes("Interstellar")) simScore += 0.40;
            if (pLower.includes("inception") && movie.title.includes("Inception")) simScore += 0.40;

            const cleanTitle = movie.title.split(" (")[0];
            const poster = LOCAL_POSTER_MAP[cleanTitle] || `https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500&auto=format&fit=crop&q=60`;
            
            const rawRating = movie.rating || 4.5;
            const normRating = rawRating / 5.0;
            const finalScore = 0.80 * Math.min(1.0, simScore) + 0.20 * normRating;

            return {
              rank: 1,
              id: movie.movieId,
              title: cleanTitle,
              year: parseInt(movie.title.match(/\((\d{4})\)/)?.[1] || "2020"),
              genres: genreList,
              overview: `An acclaimed ${genreList.join(", ")} story featuring deep thematic tension, character depth, and striking cinematography.`,
              rating: Math.round(rawRating * 2 * 10) / 10,
              vote_count: 850000,
              director: "Acclaimed Director",
              poster_path: poster,
              similarity_score: Math.round(Math.min(0.98, simScore) * 100) / 100,
              final_score: Math.round(Math.min(0.99, finalScore) * 100) / 100,
              match_reason: `Strong match for your request with ${genreList[0]} storytelling and resonant character themes.`
            };
          });

          const ranked = scored
            .sort((a, b) => (b.final_score || b.similarity_score) - (a.final_score || a.similarity_score))
            .slice(0, 12)
            .map((item, rIdx) => ({ ...item, rank: rIdx + 1 }));

          setRecommendations(ranked);
          setEnhancedQuery(prompt);
          setIsLoading(false);
        }, 800);
      } else {
        setIsLoading(false);
      }
    } catch (e) {
      setIsLoading(false);
    }
  };

  const toggleWatchlist = (id: number, title: string) => {
    let updated: number[] = [];
    if (watchlist.includes(id)) {
      updated = watchlist.filter(item => item !== id);
      showToast(`Removed "${title}" from watchlist`);
    } else {
      updated = [...watchlist, id];
      showToast(`Added "${title}" to your watchlist!`);
    }
    setWatchlist(updated);
    if (typeof window !== "undefined") {
      localStorage.setItem("cinematch_watchlist", JSON.stringify(updated));
    }
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!loginName.trim()) return;
    const updatedUser: UserProfile = {
      name: loginName,
      email: loginEmail || `${loginName.toLowerCase().replace(/\s+/g, "")}@example.com`,
      avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(loginName)}`,
      preferredGenres: ["Sci-Fi", "Thriller", "Action"],
      isLoggedIn: true
    };
    setUser(updatedUser);
    if (typeof window !== "undefined") {
      localStorage.setItem("cinematch_user", JSON.stringify(updatedUser));
    }
    setShowProfileModal(false);
    showToast(`Welcome back, ${loginName}!`);
  };

  const handleLogout = () => {
    const defaultUser: UserProfile = {
      name: "Guest User",
      email: "guest@cinematch.ai",
      avatar: "",
      preferredGenres: [],
      isLoggedIn: false
    };
    setUser(defaultUser);
    if (typeof window !== "undefined") {
      localStorage.removeItem("cinematch_user");
    }
    setShowProfileModal(false);
    showToast("Signed out successfully.");
  };

  // Filter and Sort Output
  const filteredRecs = recommendations
    .filter(m => (m.rating || 8.0) >= minRating * 2)
    .filter(m => selectedGenre === "All" || m.genres.some(g => g.toLowerCase().includes(selectedGenre.toLowerCase())))
    .sort((a, b) => {
      if (sortBy === "rating") return b.rating - a.rating;
      if (sortBy === "year") return b.year - a.year;
      return (b.similarity_score || 0) - (a.similarity_score || 0);
    });

  return (
    <div className="min-h-screen bg-[#050505] text-white flex flex-col font-sans antialiased selection:bg-red-600 selection:text-white">
      
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-3.5 rounded-xl border border-red-600/50 bg-[#111111] text-white shadow-2xl animate-fade-in">
          <AlertCircle className="w-4 h-4 text-red-500" />
          <span className="text-xs font-bold">{toastMessage}</span>
        </div>
      )}

      {/* User Login / Profile Modal */}
      {showProfileModal && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-[#111111] border border-[#262626] rounded-3xl p-6 shadow-2xl flex flex-col gap-5 relative">
            <button 
              onClick={() => setShowProfileModal(false)}
              className="absolute top-4 right-4 text-neutral-400 hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            {user.isLoggedIn ? (
              <div className="flex flex-col gap-4">
                <div className="flex items-center gap-3.5 pb-4 border-b border-[#222222]">
                  <img 
                    src={user.avatar || "https://avatars.githubusercontent.com/u/142834906?v=4"} 
                    alt={user.name} 
                    className="w-14 h-14 rounded-2xl object-cover border-2 border-red-600"
                  />
                  <div>
                    <h3 className="text-lg font-black text-white">{user.name}</h3>
                    <p className="text-xs text-neutral-400 font-medium">{user.email}</p>
                    <span className="inline-block text-[10px] font-extrabold px-2 py-0.5 rounded bg-red-950/60 text-red-400 border border-red-900/40 mt-1">
                      Member Active
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-xs font-black text-neutral-400 uppercase tracking-wider">Your Taste Profile</h4>
                  <div className="flex flex-wrap gap-1.5">
                    {["Sci-Fi", "Psychological Thriller", "Drama", "Crime", "Mystery"].map(g => (
                      <span key={g} className="text-xs font-bold px-2.5 py-1 rounded-lg bg-[#181818] border border-[#262626] text-neutral-200">
                        {g}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3.5 bg-[#161616] border border-[#242424] rounded-2xl flex items-center justify-between">
                  <span className="text-xs font-bold text-neutral-300">Saved in Watchlist</span>
                  <span className="text-xs font-black text-red-500">{watchlist.length} Movies</span>
                </div>

                <div className="flex items-center gap-2 pt-2">
                  <button
                    onClick={handleLogout}
                    className="w-full py-2.5 rounded-xl text-xs font-extrabold bg-[#1a1a1a] hover:bg-red-950/50 hover:text-red-400 text-neutral-300 border border-[#2a2a2a] transition-all cursor-pointer flex items-center justify-center gap-2"
                  >
                    <LogOut className="w-4 h-4" />
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                <div>
                  <div className="w-10 h-10 rounded-2xl bg-[#e50914] flex items-center justify-center text-white shadow-lg shadow-red-600/30 mb-3">
                    <User className="w-5 h-5" />
                  </div>
                  <h3 className="text-xl font-black text-white">Sign in to CineMatch</h3>
                  <p className="text-xs text-neutral-400 mt-1">Save your favorite movies, track recommendations, and personalize your taste profile.</p>
                </div>

                <form onSubmit={handleLoginSubmit} className="space-y-3">
                  <div>
                    <label className="text-[11px] font-extrabold text-neutral-400 uppercase block mb-1">Your Name</label>
                    <input 
                      type="text"
                      required
                      placeholder="e.g. Kaustubh Tiwari"
                      value={loginName}
                      onChange={(e) => setLoginName(e.target.value)}
                      className="w-full bg-[#181818] border border-[#262626] focus:border-red-600 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-extrabold text-neutral-400 uppercase block mb-1">Email Address</label>
                    <input 
                      type="email"
                      placeholder="e.g. yourname@example.com"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      className="w-full bg-[#181818] border border-[#262626] focus:border-red-600 rounded-xl px-3.5 py-2.5 text-xs text-white outline-none"
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full py-3 rounded-xl text-xs font-black bg-[#e50914] hover:bg-red-700 text-white uppercase tracking-wider transition-all cursor-pointer shadow-lg shadow-red-600/30 flex items-center justify-center gap-2"
                  >
                    <LogIn className="w-4 h-4" />
                    Continue
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Movie Detail Modal */}
      {selectedMovie && (
        <div className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-2xl bg-[#111111] border border-[#262626] rounded-3xl overflow-hidden shadow-2xl flex flex-col md:flex-row relative">
            <button 
              onClick={() => setSelectedMovie(null)}
              className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-black/70 border border-neutral-700 flex items-center justify-center text-neutral-300 hover:text-white cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="md:w-5/12 bg-neutral-900 relative">
              <img 
                src={selectedMovie.poster_path || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500"} 
                alt={selectedMovie.title}
                className="w-full h-full object-cover min-h-[300px]"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#111111] via-transparent to-transparent md:hidden" />
            </div>

            <div className="md:w-7/12 p-6 flex flex-col justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="text-xs font-black px-2.5 py-0.5 rounded-md bg-[#e50914] text-white">
                    #{selectedMovie.rank} Match
                  </span>
                  <span className="text-xs font-bold text-neutral-400">{selectedMovie.year}</span>
                  <span className="text-xs font-bold text-red-500 flex items-center gap-1 ml-auto">
                    <Star className="w-3.5 h-3.5 fill-red-500 text-red-500" />
                    {selectedMovie.rating} / 10
                  </span>
                </div>

                <h3 className="text-2xl font-black text-white leading-tight mb-2">{selectedMovie.title}</h3>

                <div className="flex flex-wrap gap-1.5 mb-3">
                  {selectedMovie.genres.map(g => (
                    <span key={g} className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#1c1c1c] text-neutral-300 border border-[#2a2a2a]">
                      {g}
                    </span>
                  ))}
                </div>

                <p className="text-xs text-neutral-300 leading-relaxed font-normal mb-4">
                  {selectedMovie.overview}
                </p>

                <div className="bg-[#181818] p-3.5 rounded-2xl border border-[#262626] mb-3">
                  <div className="text-[10px] font-black text-red-500 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5" /> Why this matches your prompt:
                  </div>
                  <p className="text-xs text-neutral-200 font-medium leading-normal">
                    {selectedMovie.match_reason}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] text-neutral-400">
                  <div>
                    <span className="font-bold text-neutral-500 block text-[9px] uppercase">Match Score</span>
                    <span className="text-white font-extrabold">{Math.round((selectedMovie.similarity_score || 0.85) * 100)}%</span>
                  </div>
                  <div>
                    <span className="font-bold text-neutral-500 block text-[9px] uppercase">Director</span>
                    <span className="text-white font-bold truncate block">{selectedMovie.director || "Acclaimed Director"}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2 border-t border-[#222222]">
                <button
                  onClick={() => toggleWatchlist(selectedMovie.id, selectedMovie.title)}
                  className={`flex-1 py-2.5 rounded-xl text-xs font-extrabold flex items-center justify-center gap-2 transition-all cursor-pointer ${
                    watchlist.includes(selectedMovie.id)
                      ? "bg-[#1c1c1c] border border-red-600 text-red-500"
                      : "bg-[#e50914] text-white hover:bg-red-700"
                  }`}
                >
                  <Bookmark className={`w-4 h-4 ${watchlist.includes(selectedMovie.id) ? "fill-red-500" : ""}`} />
                  {watchlist.includes(selectedMovie.id) ? "Saved in Watchlist" : "Add to Watchlist"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TOP HEADER */}
      <header className="w-full bg-[#0a0a0a] border-b border-[#1f1f1f] sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          
          {/* Logo & Clean Subtitle */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#e50914] flex items-center justify-center shadow-lg shadow-red-600/30">
              <Flame className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-black tracking-tight text-white block leading-none">CineMatch</span>
              <span className="text-[11px] text-red-500 font-bold tracking-wide">Find your match</span>
            </div>
          </div>

          {/* Right Navigation & Profile Section */}
          <div className="flex items-center gap-2.5">
            <button 
              onClick={() => showToast(`Watchlist has ${watchlist.length} saved movies.`)}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#141414] border border-[#262626] text-xs font-extrabold text-neutral-300 hover:text-white hover:border-red-600 transition-all cursor-pointer"
            >
              <Bookmark className="w-3.5 h-3.5 text-red-500" />
              <span>Watchlist ({watchlist.length})</span>
            </button>

            {/* Profile / Sign In Button */}
            <button 
              onClick={() => setShowProfileModal(true)}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-[#141414] border border-[#262626] text-xs font-extrabold text-neutral-200 hover:text-white hover:border-red-600 transition-all cursor-pointer"
            >
              {user.isLoggedIn ? (
                <>
                  <img 
                    src={user.avatar} 
                    alt={user.name} 
                    className="w-4 h-4 rounded-full object-cover"
                  />
                  <span className="hidden sm:inline">{user.name.split(" ")[0]}</span>
                </>
              ) : (
                <>
                  <User className="w-3.5 h-3.5 text-red-500" />
                  <span>Sign In</span>
                </>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* HERO & SEARCH AREA */}
      <section className="w-full bg-gradient-to-b from-[#0e0e0e] via-[#070707] to-[#050505] border-b border-[#1c1c1c] py-14 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto flex flex-col items-center text-center gap-4">

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            Describe Any Movie You Feel Like Watching.
          </h1>

          <p className="text-sm sm:text-base text-neutral-400 max-w-2xl font-medium leading-relaxed">
            Tell CineMatch your mood, vibe, or favorite plot style in everyday words, and find the perfect movie to watch tonight.
          </p>

          {/* Search Input Box */}
          <div className="w-full max-w-3xl mt-3">
            <form 
              onSubmit={(e) => { e.preventDefault(); handleSearch(); }}
              className="relative flex items-center bg-[#111111] border-2 border-[#262626] focus-within:border-red-600 rounded-2xl shadow-2xl transition-all p-2"
            >
              <Search className="w-5 h-5 text-neutral-500 ml-3 mr-2 shrink-0" />
              <input 
                type="text"
                placeholder="e.g. 'I want a dark psychological thriller with a shocking ending'..."
                value={searchPrompt}
                onChange={(e) => setSearchPrompt(e.target.value)}
                className="w-full bg-transparent py-3 text-sm text-white placeholder:text-neutral-500 outline-none font-medium"
              />
              <button
                type="submit"
                disabled={isLoading || !searchPrompt.trim()}
                className="ml-2 px-6 py-3 rounded-xl bg-[#e50914] hover:bg-red-700 disabled:opacity-40 text-white text-xs font-black uppercase tracking-wider flex items-center gap-2 cursor-pointer transition-all shadow-lg shadow-red-600/30"
              >
                {isLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <span>Find My Movie</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Example Prompt Chips */}
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
              <span className="text-[11px] font-extrabold text-neutral-500 uppercase tracking-wider mr-1">
                Try asking:
              </span>
              {EXAMPLE_CHIPS.map((chip, idx) => (
                <button
                  key={idx}
                  onClick={() => {
                    setSearchPrompt(chip);
                    handleSearch(chip);
                  }}
                  className="text-xs font-bold px-3 py-1.5 rounded-xl bg-[#141414] hover:bg-[#1f1f1f] border border-[#242424] hover:border-red-600 text-neutral-300 hover:text-white transition-all cursor-pointer text-left"
                >
                  "{chip}"
                </button>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* MAIN RESULTS SECTION */}
      <main ref={resultsRef} className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 py-8 w-full flex flex-col gap-6">
        
        {/* Loading State */}
        {isLoading && (
          <div className="bg-[#111111] border border-[#222222] rounded-3xl p-12 flex flex-col items-center justify-center gap-4 text-center">
            <div className="relative">
              <div className="w-16 h-16 rounded-full border-4 border-neutral-800 border-t-red-600 animate-spin" />
              <Flame className="w-7 h-7 text-red-500 absolute inset-0 m-auto animate-pulse" />
            </div>
            <div>
              <h3 className="text-lg font-black text-white">
                {loadingStep === "intent" && "Understanding your movie taste..."}
                {loadingStep === "embedding" && "Searching through movie catalog..."}
                {loadingStep === "ranking" && "Finding your best matches..."}
              </h3>
              <p className="text-xs text-neutral-400 mt-1 font-medium">
                Filtering across genres, mood, and ratings...
              </p>
            </div>
          </div>
        )}

        {/* Results Header & Filter Bar */}
        {!isLoading && recommendations.length > 0 && (
          <div className="flex flex-col gap-4">
            
            {/* Filter Bar */}
            <div className="bg-[#0f0f0f] border border-[#1f1f1f] p-3 rounded-2xl flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-xs font-extrabold text-neutral-500 mr-2 flex items-center gap-1">
                  <Filter className="w-3.5 h-3.5" /> Genre:
                </span>
                {["All", "Sci-Fi", "Thriller", "Drama", "Action", "Crime", "Comedy", "Romance"].map(g => (
                  <button
                    key={g}
                    onClick={() => setSelectedGenre(g)}
                    className={`text-xs font-bold px-3 py-1 rounded-lg transition-all cursor-pointer ${
                      selectedGenre === g 
                        ? "bg-[#e50914] text-white" 
                        : "bg-[#161616] text-neutral-400 hover:text-white border border-[#222222]"
                    }`}
                  >
                    {g}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 text-xs font-bold text-neutral-400">
                  <span>Sort by:</span>
                  <select 
                    value={sortBy} 
                    onChange={(e) => setSortBy(e.target.value as any)}
                    className="bg-[#181818] border border-[#262626] text-white text-xs font-bold rounded-lg px-2.5 py-1 outline-none cursor-pointer"
                  >
                    <option value="similarity">Top Match</option>
                    <option value="rating">IMDb Rating</option>
                    <option value="year">Release Year</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Movie Recommendation Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
              {filteredRecs.map((movie) => {
                const isBookmarked = watchlist.includes(movie.id);
                return (
                  <div
                    key={movie.id}
                    onClick={() => setSelectedMovie(movie)}
                    className="bg-[#111111] border border-[#222222] hover:border-red-600/70 rounded-2xl overflow-hidden flex flex-col justify-between transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-red-950/20 group cursor-pointer"
                  >
                    <div>
                      {/* Card Image Header */}
                      <div className="relative aspect-[16/10] overflow-hidden bg-neutral-900">
                        <img 
                          src={movie.poster_path || "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=500"} 
                          alt={movie.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-[#111111] via-[#111111]/20 to-transparent" />
                        
                        {/* Rank Badge */}
                        <div className="absolute top-3 left-3 bg-[#e50914] text-white text-xs font-black px-2.5 py-1 rounded-lg shadow-lg">
                          #{movie.rank}
                        </div>

                        {/* Rating Badge */}
                        <div className="absolute top-3 right-3 bg-black/75 backdrop-blur-sm text-white text-xs font-black px-2 py-1 rounded-lg border border-neutral-700 flex items-center gap-1">
                          <Star className="w-3 h-3 fill-red-500 text-red-500" />
                          <span>{movie.rating}</span>
                        </div>

                        {/* Match Percentage */}
                        <div className="absolute bottom-3 right-3 bg-red-950/80 border border-red-900/60 text-red-200 text-[10px] font-black px-2 py-0.5 rounded">
                          {Math.round((movie.similarity_score || 0.85) * 100)}% Match
                        </div>
                      </div>

                      {/* Card Body */}
                      <div className="p-4 flex flex-col gap-2.5">
                        <div>
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-base font-black text-white group-hover:text-red-400 transition-colors leading-tight">
                              {movie.title}
                            </h4>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleWatchlist(movie.id, movie.title);
                              }}
                              className="text-neutral-500 hover:text-red-500 transition-colors cursor-pointer"
                            >
                              <Bookmark className={`w-4 h-4 ${isBookmarked ? "fill-red-500 text-red-500" : ""}`} />
                            </button>
                          </div>
                          <span className="text-xs font-bold text-neutral-500">{movie.year} • {movie.genres.slice(0, 2).join(", ")}</span>
                        </div>

                        <p className="text-xs text-neutral-400 font-medium line-clamp-2 leading-relaxed">
                          {movie.overview}
                        </p>

                        {/* Why It Matches Box */}
                        <div className="bg-[#161616] p-2.5 rounded-xl border border-[#242424] mt-1">
                          <div className="text-[9px] font-black text-red-500 uppercase tracking-wider flex items-center gap-1 mb-0.5">
                            <Sparkles className="w-3 h-3" /> Why this matches:
                          </div>
                          <p className="text-[11px] text-neutral-200 font-medium line-clamp-2 leading-snug">
                            {movie.match_reason}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Card Footer */}
                    <div className="px-4 py-3 border-t border-[#1a1a1a] bg-[#0d0d0d] flex items-center justify-between text-xs font-extrabold text-neutral-400 group-hover:text-white transition-colors">
                      <span>View Details</span>
                      <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

      </main>

      {/* FOOTER */}
      <footer className="w-full bg-[#080808] border-t border-[#1a1a1a] py-8 px-4 text-center text-xs font-bold text-neutral-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-[#e50914] flex items-center justify-center text-white">
              <Flame className="w-3.5 h-3.5" />
            </div>
            <span className="text-white font-extrabold text-sm">CineMatch</span>
            <span className="text-neutral-400 font-medium">— Find your match</span>
          </div>
          <p className="text-neutral-500">© 2026 Kaustubh Tiwari. All rights reserved.</p>
        </div>
      </footer>

    </div>
  );
}
