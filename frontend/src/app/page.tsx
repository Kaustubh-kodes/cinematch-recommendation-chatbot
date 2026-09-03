"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Film, BookOpen, Sliders, Sparkles, Trash2, Plus, Check, 
  Search, Star, MessageSquare, Send, Info, Bookmark, User, 
  RefreshCw, AlertCircle, HelpCircle, Heart, X, BookOpenCheck, Flame
} from "lucide-react";

// Types
interface Recommendation {
  item_id: number;
  title: string;
  genres: string;
  score: number;
  raw_rating?: number;
  explanation?: string;
  evidence: {
    content_score: number;
    collaborative_score: number;
    preference_score: number;
    final_score: number;
    matched_genres: string[];
    similar_to: string[];
  };
}

interface Message {
  role: "user" | "assistant";
  content: string;
  preferences?: any;
  recommendations?: Recommendation[];
}

const API_URL = "http://localhost:8000";

// Mock Fallback Database in case the FastAPI backend is offline
const MOCK_MOVIES = [
  { movieId: 1, title: "Toy Story (1995)", genres: "Adventure|Animation|Children|Comedy|Fantasy" },
  { movieId: 50, title: "Usual Suspects, The (1995)", genres: "Crime|Mystery|Thriller" },
  { movieId: 110, title: "Braveheart (1995)", genres: "Action|Drama|War" },
  { movieId: 260, title: "Star Wars: Episode IV - A New Hope (1977)", genres: "Action|Adventure|Sci-Fi" },
  { movieId: 527, title: "Schindler's List (1993)", genres: "Drama|War" },
  { movieId: 589, title: "Terminator 2: Judgment Day (1991)", genres: "Action|Sci-Fi|Thriller" },
  { movieId: 858, title: "Godfather, The (1972)", genres: "Crime|Drama" },
  { movieId: 2571, title: "Matrix, The (1999)", genres: "Action|Sci-Fi|Thriller" },
  { movieId: 2959, title: "Fight Club (1999)", genres: "Action|Crime|Drama|Thriller" },
  { movieId: 4993, title: "Lord of the Rings: The Fellowship of the Ring, The (2001)", genres: "Adventure|Fantasy" },
  { movieId: 58559, title: "Dark Knight, The (2008)", genres: "Action|Crime|Drama|IMAX" },
  { movieId: 79132, title: "Inception (2010)", genres: "Action|Crime|Drama|Mystery|Sci-Fi|Thriller|IMAX" },
  { movieId: 109487, title: "Interstellar (2014)", genres: "Sci-Fi|IMAX" }
];

const MOCK_BOOKS = [
  { book_id: 1, title: "The Hunger Games", authors: "Suzanne Collins", genres: "Adventure|Sci-Fi" },
  { book_id: 2, title: "Harry Potter and the Sorcerer's Stone", authors: "J.K. Rowling", genres: "Fantasy|Classics" },
  { book_id: 3, title: "Twilight", authors: "Stephenie Meyer", genres: "Romance|Fantasy" },
  { book_id: 4, title: "To Kill a Mockingbird", authors: "Harper Lee", genres: "Classics|Drama" },
  { book_id: 5, title: "The Great Gatsby", authors: "F. Scott Fitzgerald", genres: "Classics|Drama" },
  { book_id: 6, title: "The Fault in Our Stars", authors: "John Green", genres: "Romance|Drama" },
  { book_id: 7, title: "The Hobbit", authors: "J.R.R. Tolkien", genres: "Fantasy|Adventure" },
  { book_id: 8, title: "The Catcher in the Rye", authors: "J.D. Salinger", genres: "Classics|Drama" },
  { book_id: 9, title: "Angels & Demons", authors: "Dan Brown", genres: "Mystery|Thriller" },
  { book_id: 10, title: "Pride and Prejudice", authors: "Jane Austen", genres: "Romance|Classics" }
];

export default function Home() {
  // Navigation Tabs
  const [activeTab, setActiveTab] = useState<"dashboard" | "watchlist" | "profile">("dashboard");
  
  // Media Context
  const [mediaType, setMediaType] = useState<"movie" | "book">("movie");
  
  // User Context
  const [userId, setUserId] = useState<number>(1);
  
  // Recommender Inputs
  const [itemContext, setItemContext] = useState<{ id: number; title: string } | null>(null);
  const [contentWeight, setContentWeight] = useState<number>(40);
  const [collabWeight, setCollabWeight] = useState<number>(40);
  const [prefWeight, setPrefWeight] = useState<number>(20);
  const [collabMethod, setCollabMethod] = useState<"svd" | "item_item">("svd");
  const [minRating, setMinRating] = useState<number>(0.0);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [avoidGenres, setAvoidGenres] = useState<string[]>([]);
  
  // Outputs & Lists
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [userRatings, setUserRatings] = useState<Record<number, number>>({});
  
  // Search & Auto-complete
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  
  // Chat Interface
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<Message[]>([
    {
      role: "assistant",
      content: "Welcome to CineMatch! Tell me what movies or books you're craving, and our hybrid ML engine will curate and rank tailored recommendations for you."
    }
  ]);
  
  // Status states
  const [isRecsLoading, setIsRecsLoading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState<boolean | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Check backend health
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
          setIsBackendOnline(true);
          showToast("Connected to CineMatch ML Backend!");
        } else {
          setIsBackendOnline(false);
        }
      } catch (err) {
        setIsBackendOnline(false);
        showToast("Backend Offline — Running in Local Mock Engine Mode.", true);
      }
    };
    checkHealth();
  }, []);

  // Fetch recommendations whenever inputs change
  useEffect(() => {
    fetchRecommendations();
  }, [mediaType, userId, itemContext, collabMethod, selectedGenres, avoidGenres, minRating]);

  // Adjust sliders to sum to 100
  const handleWeightChange = (type: "content" | "collab" | "pref", val: number) => {
    if (type === "content") {
      setContentWeight(val);
      const remaining = 100 - val;
      const ratio = remaining / (collabWeight + prefWeight || 1);
      setCollabWeight(Math.round(collabWeight * ratio));
      setPrefWeight(Math.round(prefWeight * ratio));
    } else if (type === "collab") {
      setCollabWeight(val);
      const remaining = 100 - val;
      const ratio = remaining / (contentWeight + prefWeight || 1);
      setContentWeight(Math.round(contentWeight * ratio));
      setPrefWeight(Math.round(prefWeight * ratio));
    } else {
      setPrefWeight(val);
      const remaining = 100 - val;
      const ratio = remaining / (contentWeight + collabWeight || 1);
      setContentWeight(Math.round(contentWeight * ratio));
      setCollabWeight(Math.round(collabWeight * ratio));
    }
  };

  // Toast notifier helper
  const showToast = (msg: string, isWarning = false) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Scroll chat window to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isChatLoading]);

  // Auto-complete Search logic
  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    
    // Filter database
    const db = mediaType === "movie" ? MOCK_MOVIES : MOCK_BOOKS;
    const matches = db.filter(item => 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (mediaType === "book" && (item as any).authors?.toLowerCase().includes(searchQuery.toLowerCase()))
    );
    
    setSearchResults(matches);
  }, [searchQuery, mediaType]);

  // Dynamic Cover Gradients - Solid Black & Vivid Red Aesthetic
  const getCoverGradient = (genres: string) => {
    const lower = genres.toLowerCase();
    if (lower.includes("sci-fi") || lower.includes("fantasy")) {
      return "from-red-950 via-zinc-950 to-black";
    }
    if (lower.includes("romance") || lower.includes("love")) {
      return "from-rose-950 via-red-950 to-black";
    }
    if (lower.includes("thriller") || lower.includes("horror") || lower.includes("crime") || lower.includes("mystery")) {
      return "from-red-900 via-neutral-950 to-black";
    }
    if (lower.includes("action") || lower.includes("adventure")) {
      return "from-red-950 via-stone-950 to-black";
    }
    if (lower.includes("comedy")) {
      return "from-rose-900 via-zinc-950 to-black";
    }
    return "from-red-950 via-zinc-950 to-black";
  };

  // Trigger Recommendations Call
  const fetchRecommendations = async () => {
    setIsRecsLoading(true);
    
    const requestPayload = {
      user_id: userId,
      item_id: itemContext?.id || null,
      preferences: {
        genres: selectedGenres,
        avoid: avoidGenres,
        minimum_rating: minRating
      },
      media_type: mediaType,
      method: collabMethod,
      top_k: 12,
      weights: {
        content: contentWeight / 100,
        collaborative: collabWeight / 100,
        preference: prefWeight / 100
      }
    };

    if (isBackendOnline) {
      try {
        const res = await fetch(`${API_URL}/recommend/hybrid`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestPayload)
        });
        if (res.ok) {
          const data = await res.json();
          setRecommendations(data.recommendations);
          setIsRecsLoading(false);
          return;
        }
      } catch (err) {
        console.error("Fetch failed, reverting to mock.", err);
      }
    }
    
    // Fallback Mock Recommendation Engine
    setTimeout(() => {
      const db = mediaType === "movie" ? MOCK_MOVIES : MOCK_BOOKS;
      const recs: Recommendation[] = [];
      const item_id_field = mediaType === "movie" ? "movieId" : "book_id";
      
      const selected = [...db].sort(() => 0.5 - Math.random()).slice(0, 8);
      
      selected.forEach((item) => {
        const itemIdVal = (item as any)[item_id_field];
        const base_score = 0.5 + Math.random() * 0.45;
        const matched = selectedGenres.length > 0 
          ? item.genres.split("|").filter(g => selectedGenres.includes(g)) 
          : [];
          
        recs.push({
          item_id: itemIdVal,
          title: item.title,
          genres: item.genres,
          score: base_score,
          raw_rating: Math.round((3.4 + Math.random() * 1.5) * 10) / 10,
          explanation: `Recommended because it aligns with your interest in ${item.genres.split('|')[0]} and your rating profile.`,
          evidence: {
            content_score: Math.round((0.4 + Math.random() * 0.5) * 100) / 100,
            collaborative_score: Math.round((0.5 + Math.random() * 0.4) * 100) / 100,
            preference_score: selectedGenres.length > 0 ? (matched.length / selectedGenres.length) : 0.0,
            final_score: Math.round(base_score * 100) / 100,
            matched_genres: matched,
            similar_to: itemContext ? [itemContext.title] : []
          }
        });
      });
      
      setRecommendations(recs);
      setIsRecsLoading(false);
    }, 400);
  };

  // Send Chat message to Conversational Layer
  const handleSendChat = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatMessage.trim()) return;
    
    const userMsg = chatMessage;
    setChatMessage("");
    
    const updatedHistory = [...chatHistory, { role: "user" as const, content: userMsg }];
    setChatHistory(updatedHistory);
    setIsChatLoading(true);
    
    if (isBackendOnline) {
      try {
        const res = await fetch(`${API_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userMsg,
            user_id: userId,
            media_type: mediaType,
            history: updatedHistory.slice(-6).map(h => ({ role: h.role, content: h.content }))
          })
        });
        
        if (res.ok) {
          const data = await res.json();
          setChatHistory(prev => [...prev, {
            role: "assistant",
            content: data.reply,
            preferences: data.preferences,
            recommendations: data.recommendations
          }]);
          
          if (data.recommendations && data.recommendations.length > 0) {
            setRecommendations(data.recommendations);
          }
          setIsChatLoading(false);
          return;
        }
      } catch (err) {
        console.error("Chat fetch failed, reverting to mock.", err);
      }
    }
    
    // Fallback Mock Conversational Engine
    setTimeout(() => {
      const promptLower = userMsg.toLowerCase();
      let detectedGenre = "Action";
      if (promptLower.includes("sci-fi") || promptLower.includes("science")) detectedGenre = "Sci-Fi";
      if (promptLower.includes("fantasy") || promptLower.includes("magic")) detectedGenre = "Fantasy";
      if (promptLower.includes("mystery") || promptLower.includes("thriller")) detectedGenre = "Mystery";
      if (promptLower.includes("romance") || promptLower.includes("love")) detectedGenre = "Romance";
      
      const db = mediaType === "movie" ? MOCK_MOVIES : MOCK_BOOKS;
      const item_id_field = mediaType === "movie" ? "movieId" : "book_id";
      
      const matches = db.filter(item => item.genres.includes(detectedGenre)).slice(0, 3);
      const recsList = matches.map(item => {
        const itemIdVal = (item as any)[item_id_field];
        const base_score = 0.78 + Math.random() * 0.18;
        return {
          item_id: itemIdVal,
          title: item.title,
          genres: item.genres,
          score: base_score,
          explanation: `Strong match grounded in ${detectedGenre} genre overlap and collaborative latent features.`,
          evidence: {
            content_score: base_score - 0.05,
            collaborative_score: 0.70,
            preference_score: 1.0,
            final_score: base_score,
            matched_genres: [detectedGenre],
            similar_to: []
          }
        };
      });
      
      const reply = `I've analyzed your preference for "${userMsg}". Our ML scoring engine identified strong signals for **${detectedGenre}** narratives. Here are the top ranked recommendations:`;
      
      setChatHistory(prev => [...prev, {
        role: "assistant",
        content: reply,
        recommendations: recsList
      }]);
      setIsChatLoading(false);
    }, 1000);
  };

  // Add/Remove Watchlist item
  const toggleWatchlist = (item: any) => {
    const isPresent = watchlist.some(w => w.item_id === item.item_id);
    if (isPresent) {
      setWatchlist(prev => prev.filter(w => w.item_id !== item.item_id));
      showToast(`Removed "${item.title}" from watchlist.`);
    } else {
      setWatchlist(prev => [...prev, item]);
      showToast(`Added "${item.title}" to watchlist!`);
    }
  };

  // Give a rating to an item
  const handleRateItem = (itemId: number, rating: number) => {
    setUserRatings(prev => ({ ...prev, [itemId]: rating }));
    showToast(`Rated item ${rating} stars! Recalculating collaborative signals...`);
    fetchRecommendations();
  };

  return (
    <div className="min-h-screen bg-black text-zinc-100 flex flex-col relative overflow-hidden selection:bg-red-600 selection:text-white">
      {/* Dynamic Crimson Glow Spots on Pure Black */}
      <div className="glow-spot top-[-120px] left-[15%] pulsing-glow" />
      <div className="glow-spot bottom-[-100px] right-[10%]" />
      
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 px-5 py-4 rounded-xl border shadow-2xl transition-all duration-300 transform translate-y-0 ${
          toastMessage.includes("Offline") 
            ? "bg-zinc-950/95 border-red-500/40 text-red-200" 
            : "bg-black/95 border-red-600/50 text-red-100 shadow-red-950/50"
        }`}>
          <AlertCircle className="w-5 h-5 text-red-500" />
          <span className="text-sm font-medium">{toastMessage}</span>
        </div>
      )}

      {/* Sleek Header */}
      <header className="border-b border-red-950/40 bg-black/85 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 via-red-500 to-rose-600 flex items-center justify-center shadow-lg shadow-red-600/30">
              <Flame className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-red-500 via-rose-400 to-red-600 bg-clip-text text-transparent">CineMatch</span>
              <span className="text-[10px] text-red-500/70 block uppercase font-mono tracking-widest leading-none">Hybrid AI Engine</span>
            </div>
          </div>
          
          {/* Main Navigation tabs */}
          <nav className="flex gap-1 bg-zinc-950 p-1 rounded-xl border border-zinc-900">
            <button 
              onClick={() => setActiveTab("dashboard")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "dashboard" ? "bg-red-600 text-white shadow-md shadow-red-600/30" : "text-zinc-400 hover:text-white"
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              Rec Engine
            </button>
            <button 
              onClick={() => setActiveTab("watchlist")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "watchlist" ? "bg-red-600 text-white shadow-md shadow-red-600/30" : "text-zinc-400 hover:text-white"
              }`}
            >
              <Bookmark className="w-3.5 h-3.5" />
              Watchlist ({watchlist.length})
            </button>
            <button 
              onClick={() => setActiveTab("profile")}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                activeTab === "profile" ? "bg-red-600 text-white shadow-md shadow-red-600/30" : "text-zinc-400 hover:text-white"
              }`}
            >
              <User className="w-3.5 h-3.5" />
              User Profile
            </button>
          </nav>

          {/* Backend status indicator */}
          <div className="flex items-center gap-2.5 bg-zinc-950 px-4 py-2 rounded-xl border border-zinc-900">
            <div className={`w-2.5 h-2.5 rounded-full ${isBackendOnline ? "bg-red-500 animate-pulse shadow-sm shadow-red-500" : "bg-zinc-600"}`} />
            <span className="text-[11px] font-semibold text-zinc-400">
              {isBackendOnline ? "ML Server Active" : "Mock Mode"}
            </span>
          </div>
        </div>
      </header>

      {/* Main Layout Area */}
      <main className="flex-1 max-w-7xl mx-auto px-6 py-8 w-full flex flex-col lg:flex-row gap-8 relative z-10">
        
        {/* Tab 1: Dashboard */}
        {activeTab === "dashboard" && (
          <>
            {/* Left Column: recommendation Configuration & Search */}
            <div className="flex-1 flex flex-col gap-6">
              
              {/* Profile Config Row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Media Select Card */}
                <div className="glass-panel p-5 rounded-2xl flex flex-col gap-4 bg-[#0a0a0a]/90 border border-red-950/30 shadow-xl">
                  <h3 className="text-sm font-bold text-zinc-200 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-red-500" />
                    1. Choose Media & Target
                  </h3>
                  
                  {/* Media buttons */}
                  <div className="grid grid-cols-2 gap-3">
                    <button 
                      onClick={() => { setMediaType("movie"); setItemContext(null); }}
                      className={`flex items-center justify-center gap-2.5 py-3 rounded-xl border text-sm font-semibold transition-all ${
                        mediaType === "movie" 
                          ? "bg-red-950/40 border-red-600 text-red-100 shadow-[inset_0_1px_15px_rgba(239,68,68,0.25)]" 
                          : "border-zinc-800 bg-zinc-950 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                      }`}
                    >
                      <Film className="w-4 h-4" />
                      Movies
                    </button>
                    <button 
                      onClick={() => { setMediaType("book"); setItemContext(null); }}
                      className={`flex items-center justify-center gap-2.5 py-3 rounded-xl border text-sm font-semibold transition-all ${
                        mediaType === "book" 
                          ? "bg-red-950/40 border-red-600 text-red-100 shadow-[inset_0_1px_15px_rgba(239,68,68,0.25)]" 
                          : "border-zinc-800 bg-zinc-950 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                      }`}
                    >
                      <BookOpen className="w-4 h-4" />
                      Books
                    </button>
                  </div>
                  
                  {/* Search Autocomplete */}
                  <div className="relative">
                    <div className="flex items-center bg-zinc-950 rounded-xl border border-zinc-800 focus-within:border-red-600/60 px-3 transition-colors">
                      <Search className="w-4 h-4 text-zinc-500 mr-2" />
                      <input 
                        type="text"
                        placeholder={`Search ${mediaType} to seed context...`}
                        value={searchQuery}
                        onChange={(e) => { setSearchQuery(e.target.value); setShowDropdown(true); }}
                        className="bg-transparent text-sm w-full py-2.5 outline-none text-zinc-200 placeholder:text-zinc-600"
                      />
                      {searchQuery && (
                        <button onClick={() => { setSearchQuery(""); setItemContext(null); }} className="text-zinc-500 hover:text-white">
                          <X className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                    
                    {/* Autocomplete list */}
                    {showDropdown && searchResults.length > 0 && (
                      <div className="absolute top-full left-0 right-0 mt-2 bg-black border border-red-900/40 rounded-xl max-h-52 overflow-y-auto z-50 shadow-2xl">
                        {searchResults.map((item, idx) => {
                          const iid = mediaType === "movie" ? item.movieId : item.book_id;
                          return (
                            <button
                              key={idx}
                              onClick={() => {
                                setItemContext({ id: iid, title: item.title });
                                setSearchQuery(item.title);
                                setShowDropdown(false);
                              }}
                              className="w-full text-left px-4 py-3 text-xs hover:bg-red-950/50 hover:text-red-200 border-b border-zinc-900 last:border-0 text-zinc-300 block transition-colors"
                            >
                              <span className="font-bold block text-sm">{item.title}</span>
                              <span className="text-[10px] text-zinc-500 block">{item.genres}</span>
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                  
                  {/* Context Item display */}
                  {itemContext && (
                    <div className="bg-red-950/30 border border-red-600/30 px-4 py-3 rounded-xl flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-red-400" />
                        <span className="text-xs font-semibold text-red-300">Similarity context: <strong className="text-zinc-100">{itemContext.title}</strong></span>
                      </div>
                      <button onClick={() => { setItemContext(null); setSearchQuery(""); }} className="text-zinc-400 hover:text-white text-xs">Clear</button>
                    </div>
                  )}
                </div>
                
                {/* Sliders Card */}
                <div className="glass-panel p-5 rounded-2xl flex flex-col gap-4 bg-[#0a0a0a]/90 border border-red-950/30 shadow-xl">
                  <h3 className="text-sm font-bold text-zinc-200 flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-red-500" />
                    2. Configure Hybrid Weights
                  </h3>
                  
                  {/* Slider controls */}
                  <div className="flex flex-col gap-3">
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-xs font-bold text-zinc-400">
                        <span>Content Similarity</span>
                        <span className="text-red-400 font-mono">{contentWeight}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="100" value={contentWeight}
                        onChange={(e) => handleWeightChange("content", parseInt(e.target.value))}
                        className="w-full h-1.5 bg-zinc-900 rounded-lg appearance-none cursor-pointer accent-red-600"
                      />
                    </div>
                    
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-xs font-bold text-zinc-400">
                        <span>Collaborative Signals (SVD)</span>
                        <span className="text-red-400 font-mono">{collabWeight}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="100" value={collabWeight}
                        onChange={(e) => handleWeightChange("collab", parseInt(e.target.value))}
                        className="w-full h-1.5 bg-zinc-900 rounded-lg appearance-none cursor-pointer accent-red-600"
                      />
                    </div>
                    
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-xs font-bold text-zinc-400">
                        <span>Genre Preferences</span>
                        <span className="text-red-400 font-mono">{prefWeight}%</span>
                      </div>
                      <input 
                        type="range" min="0" max="100" value={prefWeight}
                        onChange={(e) => handleWeightChange("pref", parseInt(e.target.value))}
                        className="w-full h-1.5 bg-zinc-900 rounded-lg appearance-none cursor-pointer accent-red-600"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Filtering Controls panel */}
              <div className="glass-panel p-5 rounded-2xl flex flex-col md:flex-row gap-6 justify-between items-start md:items-center bg-[#0a0a0a]/90 border border-red-950/30">
                
                {/* Genre Selector */}
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest">Target Genres:</span>
                  {["Sci-Fi", "Action", "Romance", "Comedy", "Fantasy", "Mystery", "Classics"].map((genre) => {
                    const isSelected = selectedGenres.includes(genre);
                    return (
                      <button
                        key={genre}
                        onClick={() => {
                          setSelectedGenres(prev => 
                            isSelected ? prev.filter(g => g !== genre) : [...prev, genre]
                          );
                        }}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                          isSelected 
                            ? "bg-red-600 border-red-500 text-white shadow-md shadow-red-600/30" 
                            : "bg-zinc-950 border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700"
                        }`}
                      >
                        {genre}
                      </button>
                    );
                  })}
                </div>
                
                {/* Advanced parameters selectors */}
                <div className="flex items-center gap-4 w-full md:w-auto">
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase">CF Algorithm</span>
                    <select 
                      value={collabMethod} 
                      onChange={(e: any) => setCollabMethod(e.target.value)}
                      className="bg-zinc-950 border border-zinc-800 text-xs text-zinc-300 font-semibold px-3 py-2 rounded-lg outline-none focus:border-red-600/60"
                    >
                      <option value="svd" className="bg-black">Latent SVD</option>
                      <option value="item_item" className="bg-black">Item-Item CF</option>
                    </select>
                  </div>
                  
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase">Rating Cutoff</span>
                    <select 
                      value={minRating} 
                      onChange={(e: any) => setMinRating(parseFloat(e.target.value))}
                      className="bg-zinc-950 border border-zinc-800 text-xs text-zinc-300 font-semibold px-3 py-2 rounded-lg outline-none focus:border-red-600/60"
                    >
                      <option value="0.0" className="bg-black">No Limit</option>
                      <option value="3.0" className="bg-black">3+ Stars</option>
                      <option value="4.0" className="bg-black">4+ Stars</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Recommendation Grid */}
              <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center">
                  <h2 className="text-lg font-bold text-zinc-100 flex items-center gap-2.5">
                    <Flame className="w-5 h-5 text-red-500" />
                    Top Recommendations
                  </h2>
                  <button 
                    onClick={fetchRecommendations}
                    className="flex items-center gap-2 text-xs font-bold text-zinc-400 hover:text-white px-3 py-2 rounded-lg border border-zinc-800 bg-zinc-950 hover:border-red-900/50 transition-all"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isRecsLoading ? "animate-spin text-red-500" : ""}`} />
                    Refresh Engine
                  </button>
                </div>
                
                {isRecsLoading ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                      <div key={i} className="glass-panel h-80 rounded-2xl animate-pulse flex flex-col p-4 gap-3 bg-zinc-950 border-zinc-900">
                        <div className="h-40 rounded-xl bg-zinc-900 w-full" />
                        <div className="h-6 rounded bg-zinc-900 w-3/4" />
                        <div className="h-4 rounded bg-zinc-900 w-1/2" />
                      </div>
                    ))}
                  </div>
                ) : recommendations.length === 0 ? (
                  <div className="glass-panel p-16 rounded-2xl text-center flex flex-col items-center gap-3 bg-[#0a0a0a] border-zinc-900">
                    <AlertCircle className="w-12 h-12 text-zinc-700" />
                    <h3 className="text-base font-bold text-zinc-300">No matches found</h3>
                    <p className="text-xs text-zinc-500 max-w-sm">No items match the specific genre limits or rating thresholds. Try checking different genre tags or clearing the search seed.</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
                    {recommendations.map((rec) => {
                      const inWatchlist = watchlist.some(w => w.item_id === rec.item_id);
                      return (
                        <div 
                          key={rec.item_id}
                          className="glass-panel rounded-2xl overflow-hidden flex flex-col group bg-[#0a0a0a] border-zinc-900 hover:border-red-600/50 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-2xl hover:shadow-red-950/30 relative"
                        >
                          {/* Gradient Graphic Header */}
                          <div className={`h-36 bg-gradient-to-br ${getCoverGradient(rec.genres)} p-4 flex flex-col justify-between relative`}>
                            {/* Score Pill */}
                            <div className="flex justify-between items-start">
                              <span className="bg-black/85 backdrop-blur-md border border-red-500/30 px-2.5 py-1 rounded-full text-[10px] font-bold text-red-200 uppercase tracking-wider flex items-center gap-1">
                                <Sparkles className="w-3 h-3 text-red-400" />
                                {Math.round(rec.score * 100)}% Match
                              </span>
                              
                              {/* Watchlist toggle */}
                              <button 
                                onClick={() => toggleWatchlist(rec)}
                                className={`w-8 h-8 rounded-full flex items-center justify-center border backdrop-blur-md transition-all ${
                                  inWatchlist 
                                    ? "bg-red-600 border-red-500 text-white" 
                                    : "bg-black/60 border-zinc-800 text-zinc-400 hover:text-white hover:bg-red-950/60 hover:border-red-600/40"
                                }`}
                              >
                                <Bookmark className="w-4 h-4" />
                              </button>
                            </div>
                            
                            {/* Rating badge */}
                            <div className="flex justify-between items-end">
                              <span className="text-[10px] text-zinc-400 bg-black/60 px-2 py-1 rounded backdrop-blur-sm font-semibold border border-zinc-900">
                                {mediaType === "movie" ? "Movie ID: " : "Book ID: "}{rec.item_id}
                              </span>
                              {rec.raw_rating && (
                                <span className="bg-red-600 text-white px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 shadow-sm shadow-red-950">
                                  <Star className="w-3 h-3 fill-white" />
                                  {rec.raw_rating}
                                </span>
                              )}
                            </div>
                          </div>
                          
                          {/* Metadata & rating details */}
                          <div className="p-4 flex-1 flex flex-col justify-between gap-3">
                            <div className="flex flex-col gap-1.5">
                              <h4 className="text-sm font-bold text-zinc-200 line-clamp-1 group-hover:text-red-400 transition-colors">{rec.title}</h4>
                              <p className="text-[11px] text-zinc-500 line-clamp-1 flex items-center gap-1">
                                {rec.genres.replace("|", " • ")}
                              </p>
                            </div>
                            
                            {/* Score Breakdown (evidence details) */}
                            <div className="bg-black/70 border border-zinc-900 rounded-xl p-2.5 flex flex-col gap-1">
                              <span className="text-[9px] font-bold text-red-500/80 uppercase tracking-widest mb-0.5">Scoring Breakdown</span>
                              <div className="flex justify-between text-[10px] text-zinc-400">
                                <span>Content Similarity:</span>
                                <span className="font-semibold text-zinc-200 font-mono">{Math.round(rec.evidence.content_score * 100)}%</span>
                              </div>
                              <div className="flex justify-between text-[10px] text-zinc-400">
                                <span>Collaborative Signal:</span>
                                <span className="font-semibold text-zinc-200 font-mono">{Math.round(rec.evidence.collaborative_score * 100)}%</span>
                              </div>
                              <div className="flex justify-between text-[10px] text-zinc-400">
                                <span>Preference Match:</span>
                                <span className="font-semibold text-zinc-200 font-mono">{Math.round(rec.evidence.preference_score * 100)}%</span>
                              </div>
                            </div>
                            
                            {/* Explanations bubble */}
                            {rec.explanation && (
                              <p className="text-[11px] text-zinc-400 italic bg-red-950/20 p-2 rounded-lg border border-red-900/30">
                                "{rec.explanation}"
                              </p>
                            )}

                            {/* User interactive Rating */}
                            <div className="flex items-center justify-between border-t border-zinc-900 pt-3">
                              <span className="text-[10px] font-bold text-zinc-500 uppercase">Rate:</span>
                              <div className="flex gap-0.5">
                                {[1, 2, 3, 4, 5].map((stars) => {
                                  const givenRating = userRatings[rec.item_id] || 0;
                                  return (
                                    <button 
                                      key={stars} 
                                      onClick={() => handleRateItem(rec.item_id, stars)}
                                      className="text-zinc-700 hover:text-red-500 transition-colors"
                                    >
                                      <Star className={`w-3.5 h-3.5 ${stars <= givenRating ? "text-red-500 fill-red-500" : ""}`} />
                                    </button>
                                  );
                                })}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>

            {/* Right Column: AI Chat Panel */}
            <div className="w-full lg:w-96 glass-panel rounded-2xl flex flex-col h-[750px] bg-[#0a0a0a]/95 border border-red-950/40 shadow-2xl relative">
              
              {/* Sidebar Header */}
              <div className="p-4 border-b border-red-950/40 bg-black/70 backdrop-blur-md flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-red-600 flex items-center justify-center shadow-md shadow-red-600/30">
                    <MessageSquare className="w-4 h-4 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-zinc-200 block uppercase font-mono tracking-widest leading-none">CineMatch AI</h3>
                    <span className="text-[10px] text-zinc-500">Conversational Layer</span>
                  </div>
                </div>
                <HelpCircle className="w-4 h-4 text-zinc-600 cursor-help" />
              </div>
              
              {/* Message scroll container */}
              <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4">
                {chatHistory.map((msg, index) => (
                  <div 
                    key={index}
                    className={`flex flex-col gap-1.5 max-w-[85%] ${msg.role === "user" ? "ml-auto items-end" : "mr-auto items-start"}`}
                  >
                    <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                      {msg.role === "user" ? "You" : "CineMatch AI"}
                    </span>
                    <div className={`p-3 rounded-2xl text-xs leading-normal shadow-lg ${
                      msg.role === "user" 
                        ? "bg-red-600 text-white rounded-br-none shadow-red-950/40" 
                        : "bg-zinc-950 border border-zinc-800/80 text-zinc-300 rounded-bl-none"
                    }`}>
                      <p>{msg.content}</p>
                      
                      {/* Embedded chat recommendations */}
                      {msg.recommendations && msg.recommendations.length > 0 && (
                        <div className="mt-3 flex flex-col gap-2 border-t border-white/10 pt-2.5">
                          {msg.recommendations.map((rec) => (
                            <button
                              key={rec.item_id}
                              onClick={() => setItemContext({ id: rec.item_id, title: rec.title })}
                              className="w-full text-left p-2 rounded-lg bg-black/60 border border-zinc-800 hover:border-red-600/40 flex items-center justify-between text-zinc-300 hover:text-white transition-all"
                            >
                              <div>
                                <span className="font-bold block text-[11px] line-clamp-1">{rec.title}</span>
                                <span className="text-[9px] text-zinc-500 block">{rec.genres}</span>
                              </div>
                              <span className="bg-red-950 border border-red-800 text-[9px] font-bold px-2 py-0.5 rounded text-red-300 font-mono">
                                {Math.round(rec.score * 100)}%
                              </span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                
                {isChatLoading && (
                  <div className="mr-auto items-start max-w-[80%] flex flex-col gap-1">
                    <span className="text-[9px] font-bold text-zinc-500 uppercase">CineMatch AI</span>
                    <div className="p-3.5 rounded-2xl bg-zinc-950 border border-zinc-800 rounded-bl-none flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce" />
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                      <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                    </div>
                  </div>
                )}
                
                <div ref={chatEndRef} />
              </div>
              
              {/* Chat Input form */}
              <form onSubmit={handleSendChat} className="p-4 border-t border-red-950/40 bg-black/80 flex gap-2">
                <input 
                  type="text"
                  placeholder="Ask for recommendations..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  disabled={isChatLoading}
                  className="bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 outline-none px-4 py-3 rounded-xl flex-1 focus:border-red-600/60 transition-colors placeholder:text-zinc-600"
                />
                <button 
                  type="submit" 
                  disabled={isChatLoading || !chatMessage.trim()}
                  className="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-red-500 transition-all shadow-md shadow-red-600/30"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </>
        )}

        {/* Tab 2: Watchlist */}
        {activeTab === "watchlist" && (
          <div className="flex-1 flex flex-col gap-6">
            <h2 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
              <Bookmark className="w-5 h-5 text-red-500" />
              Your Personal Watchlist ({watchlist.length})
            </h2>
            
            {watchlist.length === 0 ? (
              <div className="glass-panel p-20 rounded-3xl text-center flex flex-col items-center gap-4 bg-[#0a0a0a] border-zinc-900">
                <Bookmark className="w-16 h-16 text-zinc-800" />
                <h3 className="text-lg font-bold text-zinc-300">Your Watchlist is empty</h3>
                <p className="text-xs text-zinc-500 max-w-sm">Items you bookmark while browsing recommendations will appear here. Rate them to dynamically update collaborative recommendations!</p>
                <button 
                  onClick={() => setActiveTab("dashboard")}
                  className="bg-red-600 hover:bg-red-500 text-xs font-bold text-white px-5 py-3 rounded-xl transition-all shadow-lg shadow-red-600/30"
                >
                  Browse Recommendations
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {watchlist.map((item) => (
                  <div key={item.item_id} className="glass-panel rounded-2xl overflow-hidden flex flex-col bg-[#0a0a0a] border-zinc-900 hover:border-red-600/40 transition-all">
                    <div className={`h-28 bg-gradient-to-br ${getCoverGradient(item.genres)} p-3 flex justify-between items-start`}>
                      <span className="bg-black/80 px-2 py-0.5 rounded text-[10px] font-bold text-zinc-400 border border-zinc-800">
                        ID: {item.item_id}
                      </span>
                      <button 
                        onClick={() => toggleWatchlist(item)}
                        className="w-8 h-8 rounded-full bg-black/80 border border-zinc-800 text-zinc-400 hover:text-red-400 flex items-center justify-center transition-all"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                    <div className="p-4 flex-1 flex flex-col justify-between gap-3">
                      <div>
                        <h4 className="text-sm font-bold text-zinc-200 line-clamp-1">{item.title}</h4>
                        <p className="text-[10px] text-zinc-500 mt-1">{item.genres}</p>
                      </div>
                      
                      {/* Star ratings */}
                      <div className="flex items-center justify-between border-t border-zinc-900 pt-3">
                        <span className="text-[9px] font-bold text-zinc-500">Your Rating:</span>
                        <div className="flex gap-0.5">
                          {[1, 2, 3, 4, 5].map((stars) => {
                            const given = userRatings[item.item_id] || 0;
                            return (
                              <button 
                                key={stars} 
                                onClick={() => handleRateItem(item.item_id, stars)}
                                className="text-zinc-700 hover:text-red-500 transition-colors"
                              >
                                <Star className={`w-3 h-3 ${stars <= given ? "text-red-500 fill-red-500" : ""}`} />
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: User Profile */}
        {activeTab === "profile" && (
          <div className="flex-1 glass-panel p-8 rounded-3xl border border-red-950/30 bg-[#0a0a0a] shadow-2xl flex flex-col gap-8">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-red-600 via-red-500 to-rose-700 flex items-center justify-center text-white text-2xl font-bold shadow-lg shadow-red-600/30">
                U{userId}
              </div>
              <div>
                <h2 className="text-xl font-bold text-zinc-100">User Profile Context</h2>
                <p className="text-xs text-zinc-500">Configure simulated user context for SVD/Item-Item collaborative filtering simulations.</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 border-t border-zinc-900 pt-8">
              
              {/* Simulated User ID Configuration */}
              <div className="flex flex-col gap-4">
                <h3 className="text-sm font-bold text-zinc-300 flex items-center gap-2">
                  <User className="w-4 h-4 text-red-500" />
                  Simulate User ID
                </h3>
                <p className="text-xs text-zinc-500">Enter a user ID from the dataset (Movies supports 1-610, Goodreads supports 1-2000) to pull user collaborative ratings predictions.</p>
                <div className="flex gap-2">
                  <input 
                    type="number"
                    value={userId}
                    onChange={(e) => setUserId(Math.max(1, parseInt(e.target.value) || 1))}
                    className="bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 outline-none px-4 py-3 rounded-xl w-32 focus:border-red-600/60"
                  />
                  <button 
                    onClick={() => {
                      fetchRecommendations();
                      showToast(`Switched user context to User ${userId}!`);
                    }}
                    className="bg-red-600 hover:bg-red-500 text-xs font-bold text-white px-5 rounded-xl transition-all shadow-md shadow-red-600/20"
                  >
                    Sync User Profile
                  </button>
                </div>
              </div>
              
              {/* Profile statistics */}
              <div className="flex flex-col gap-4">
                <h3 className="text-sm font-bold text-zinc-300 flex items-center gap-2">
                  <Info className="w-4 h-4 text-red-500" />
                  Profile Stats
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-zinc-950/60 border border-zinc-900 p-4 rounded-xl text-center">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Watchlist Items</span>
                    <span className="text-xl font-bold text-red-400 block mt-1 font-mono">{watchlist.length}</span>
                  </div>
                  <div className="bg-zinc-950/60 border border-zinc-900 p-4 rounded-xl text-center">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Ratings Given</span>
                    <span className="text-xl font-bold text-red-400 block mt-1 font-mono">{Object.keys(userRatings).length}</span>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Rating histories */}
            {Object.keys(userRatings).length > 0 && (
              <div className="border-t border-zinc-900 pt-8 flex flex-col gap-4">
                <h3 className="text-sm font-bold text-zinc-300">Simulated Rating History</h3>
                <div className="flex flex-wrap gap-3">
                  {Object.entries(userRatings).map(([iid, rating]) => (
                    <div key={iid} className="bg-zinc-950 border border-zinc-800 px-3 py-2 rounded-xl flex items-center gap-3 text-xs">
                      <span className="text-zinc-400">Item {iid}</span>
                      <div className="flex text-red-500">
                        {Array.from({ length: rating }).map((_, idx) => (
                          <Star key={idx} className="w-3 h-3 fill-red-500" />
                        ))}
                      </div>
                      <button 
                        onClick={() => {
                          setUserRatings(prev => {
                            const copy = { ...prev };
                            delete copy[parseInt(iid)];
                            return copy;
                          });
                        }} 
                        className="text-zinc-500 hover:text-red-400 transition-colors"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer banner */}
      <footer className="border-t border-red-950/30 bg-black py-6 text-center text-xs text-zinc-600 relative z-10">
        <p>© 2026 CineMatch. Powered by Sparse TF-IDF Cosine Similarity & SVD Latent Factorizations.</p>
      </footer>
    </div>
  );
}
