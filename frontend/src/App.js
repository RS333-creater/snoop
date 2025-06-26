import React, { useState, useEffect, useCallback, useMemo } from 'react';

// アイコンライブラリ (Lucide React)
// 本番環境では npm install lucide-react でインストールします
const CheckCircle = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
    <polyline points="22 4 12 14.01 9 11.01" />
  </svg>
);
const PlusCircle = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <line x1="12" y1="8" x2="12" y2="16" />
    <line x1="8" y1="12" x2="16" y2="12" />
  </svg>
);
const LogOut = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" />
    <line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);
const TrendingUp = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
        <polyline points="16 7 22 7 22 13" />
    </svg>
);


// --- APIクライアント ---
const API_URL = 'http://127.0.0.1:8000'; // あなたのFastAPIサーバーのアドレス

const apiClient = {
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/token`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'ログインに失敗しました。' }));
      throw new Error(errorData.detail);
    }
    return response.json();
  },

  async register(name, email, password) {
    const response = await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'ユーザー登録に失敗しました。' }));
      throw new Error(errorData.detail);
    }
    return response.json();
  },

  async getMe(token) {
    const response = await fetch(`${API_URL}/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error('ユーザー情報の取得に失敗しました。');
    }
    return response.json();
  },

  async getHabits(token) {
    const response = await fetch(`${API_URL}/habits`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error('習慣リストの取得に失敗しました。');
    }
    return response.json();
  },
  
  async createHabit(token, name, description) {
    const response = await fetch(`${API_URL}/habits`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
    });
    if (!response.ok) {
        throw new Error('習慣の作成に失敗しました。');
    }
    return response.json();
  },

  async getHabitRecords(token, habitId, startDate, endDate) {
    const response = await fetch(`${API_URL}/habits/${habitId}/records?start_date=${startDate}&end_date=${endDate}`, {
        headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!response.ok) {
        throw new Error('習慣記録の取得に失敗しました。');
    }
    return response.json();
  },
};

// --- 認証ページコンポーネント ---
function LoginPage({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('password123');
  const [name, setName] = useState('テストユーザー');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (isLogin) {
        const data = await apiClient.login(email, password);
        onLoginSuccess(data.access_token);
      } else {
        await apiClient.register(name, email, password);
        const data = await apiClient.login(email, password);
        onLoginSuccess(data.access_token);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="w-full max-w-md p-8 space-y-8 bg-gray-800 rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-4xl font-extrabold text-white">Snoopへようこそ</h2>
          <p className="mt-2 text-gray-400">
            {isLogin ? 'あなたの習慣を管理しましょう' : '新しいアカウントを作成'}
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="名前"
              required
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          )}
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="メールアドレス"
            required
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="パスワード"
            required
            className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          {error && <p className="text-red-400 text-sm text-center">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 font-semibold text-white bg-indigo-600 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-indigo-500 disabled:bg-indigo-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '処理中...' : (isLogin ? 'ログイン' : '登録')}
          </button>
        </form>
        <p className="text-sm text-center text-gray-400">
          {isLogin ? 'アカウントをお持ちでないですか？' : 'すでにアカウントをお持ちですか？'}
          <button onClick={() => setIsLogin(!isLogin)} className="ml-2 font-semibold text-indigo-400 hover:text-indigo-300">
            {isLogin ? '登録' : 'ログイン'}
          </button>
        </p>
      </div>
    </div>
  );
}


// --- メインアプリケーションコンポーネント ---
function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // 初回ロード時にトークンを検証
  useEffect(() => {
    const initApp = async () => {
      const storedToken = localStorage.getItem('habit-tracker-token');
      if (storedToken) {
        setToken(storedToken);
        try {
          const userData = await apiClient.getMe(storedToken);
          setUser(userData);
        } catch (error) {
          console.error("Token validation failed:", error);
          handleLogout();
        }
      }
      setIsLoading(false);
    };
    initApp();
  }, []);

  const handleLoginSuccess = (newToken) => {
    localStorage.setItem('habit-tracker-token', newToken);
    setToken(newToken);
    setIsLoading(true);
    const fetchUser = async () => {
      try {
        const userData = await apiClient.getMe(newToken);
        setUser(userData);
      } catch (error) {
        console.error(error);
        handleLogout();
      } finally {
        setIsLoading(false);
      }
    };
    fetchUser();
  };

  const handleLogout = () => {
    localStorage.removeItem('habit-tracker-token');
    setToken(null);
    setUser(null);
  };

  if (isLoading) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">ロード中...</div>;
  }
  
  if (!token || !user) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return <HomePage user={user} token={token} onLogout={handleLogout} />;
}

// --- ★★★ 新しいホームページコンポーネント ★★★ ---
function HomePage({ user, token, onLogout }) {
  const [habits, setHabits] = useState([]);
  const [isLoadingHabits, setIsLoadingHabits] = useState(true);

  useEffect(() => {
    const fetchHabits = async () => {
      setIsLoadingHabits(true);
      try {
        const habitsData = await apiClient.getHabits(token);
        setHabits(habitsData);
      } catch (error) {
        console.error("Failed to fetch habits:", error);
        // ここでエラーメッセージをユーザーに表示することもできます
      } finally {
        setIsLoadingHabits(false);
      }
    };
    fetchHabits();
  }, [token]);

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <Header user={user} onLogout={onLogout} />
      <main className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-bold tracking-tight">ダッシュボード</h2>
        </div>

        {isLoadingHabits ? (
          <p>習慣を読み込み中...</p>
        ) : habits.length === 0 ? (
          <div className="text-center py-12 bg-gray-800 rounded-lg">
            <p className="text-gray-400">まだ習慣が登録されていません。</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {habits.map(habit => (
              <HabitProgressCard key={habit.id} habit={habit} token={token} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

// --- ヘッダー ---
function Header({ user, onLogout }) {
  return (
    <header className="bg-gray-800/50 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-white">Snoop</h1>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-gray-300">こんにちは、{user.name}さん</span>
            <button onClick={onLogout} className="p-2 rounded-full text-gray-400 hover:text-white hover:bg-gray-700 transition-colors">
              <LogOut className="h-6 w-6" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}

// --- ★★★ 新しい習慣プログレスカードコンポーネント ★★★ ---
function HabitProgressCard({ habit, token }) {
  const [progress, setProgress] = useState({ completed: 0, total: 31 });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchJanuaryProgress = async () => {
      setIsLoading(true);
      const year = new Date().getFullYear(); // 今年（または任意の年）
      const startDate = `${year}-01-01`;
      const endDate = `${year}-01-31`;

      try {
        const records = await apiClient.getHabitRecords(token, habit.id, startDate, endDate);
        const completedCount = records.filter(r => r.status).length;
        setProgress({ completed: completedCount, total: 31 });
      } catch (error) {
        console.error(`Failed to fetch records for habit ${habit.id}:`, error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchJanuaryProgress();
  }, [habit.id, token]);

  const percentage = isLoading ? 0 : Math.round((progress.completed / progress.total) * 100);

  return (
    <div className="bg-gray-800 p-6 rounded-lg transition-all duration-200 hover:bg-gray-700/80">
        <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white">{habit.name}</h3>
            <TrendingUp className="h-6 w-6 text-gray-500"/>
        </div>
        <p className="text-gray-400 mt-2 text-sm h-10">{habit.description || '詳細がありません'}</p>
        
        <div className="mt-4">
            <div className="flex justify-between items-center text-sm mb-1">
                <span className="font-semibold text-indigo-400">1月の進捗</span>
                {isLoading ? (
                    <span className="text-gray-500">計算中...</span>
                ) : (
                    <span className="text-white font-bold">{progress.completed} / {progress.total} 日</span>
                )}
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${percentage}%`, transition: 'width 0.5s ease-in-out' }}></div>
            </div>
        </div>
    </div>
  );
}

export default App;
