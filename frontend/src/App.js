import React, { useState, useEffect, useCallback } from 'react';

// --- アイコンコンポーネント ---
const PlusCircle = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="16" /><line x1="8" y1="12" x2="16" y2="12" />
  </svg>
);
const LogOut = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" /><polyline points="16 17 21 12 16 7" /><line x1="21" y1="12" x2="9" y2="12" />
  </svg>
);
const TrendingUp = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" /><polyline points="16 7 22 7 22 13" />
    </svg>
);
const ChevronLeft = (props) => (
  <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="15 18 9 12 15 6" />
  </svg>
);
const Save = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
        <polyline points="17 21 17 13 7 13 7 21" />
        <polyline points="7 3 7 8 15 8" />
    </svg>
);
const Trash2 = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="3 6 5 6 21 6" />
        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        <line x1="10" y1="11" x2="10" y2="17" />
        <line x1="14" y1="11" x2="14" y2="17" />
    </svg>
);
const Bell = (props) => (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
        <path d="M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
);

// --- APIクライアント ---
const API_URL = 'http://127.0.0.1:8000';

const apiClient = {
  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await fetch(`${API_URL}/token`, { method: 'POST', body: formData });
    if (!response.ok) { const d = await response.json().catch(()=>({detail:'ログインに失敗しました。'})); throw new Error(d.detail); }
    return response.json();
  },
  async register(name, email, password) {
    const response = await fetch(`${API_URL}/users`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, email, password }) });
    if (!response.ok) { const d = await response.json().catch(()=>({detail:'登録に失敗しました。'})); throw new Error(d.detail); }
    return response.json();
  },
  async verifyUser(email, code) {
    const response = await fetch(`${API_URL}/users/verify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, code }) });
    if (!response.ok) { const d = await response.json().catch(()=>({detail:'認証に失敗しました。'})); throw new Error(d.detail); }
    return response.json();
  },
  async getMe(token) {
    const response = await fetch(`${API_URL}/users/me`, { headers: { 'Authorization': `Bearer ${token}` } });
    if (!response.ok) { throw new Error('ユーザー情報の取得に失敗しました。'); }
    return response.json();
  },
  async getHabits(token) {
    const response = await fetch(`${API_URL}/habits`, { headers: { 'Authorization': `Bearer ${token}` } });
    if (!response.ok) { throw new Error('習慣リストの取得に失敗しました。'); }
    return response.json();
  },
  async createHabit(token, name, description) {
    const response = await fetch(`${API_URL}/habits`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description }),
    });
    if (!response.ok) { throw new Error('習慣の作成に失敗しました。'); }
    return response.json();
  },
  async updateHabit(token, habitId, name, description) {
    const response = await fetch(`${API_URL}/habits/${habitId}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description }),
    });
    if (!response.ok) { throw new Error('習慣の更新に失敗しました。'); }
    return response.json();
  },
  async deleteHabit(token, habitId) {
    const response = await fetch(`${API_URL}/habits/${habitId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
    });
    if (response.status !== 204) {
        throw new Error('習慣の削除に失敗しました。');
    }
    return true;
  },
  async getHabitRecords(token, habitId, startDate, endDate) {
    const response = await fetch(`${API_URL}/habits/${habitId}/records?start_date=${startDate}&end_date=${endDate}`, { headers: { 'Authorization': `Bearer ${token}` } });
    if (!response.ok) { throw new Error('習慣記録の取得に失敗しました。'); }
    return response.json();
  },
  async createNotification(token, habitId, time) {
    const response = await fetch(`${API_URL}/notifications`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ habit_id: habitId, time: time, enabled: true }),
    });
    if (!response.ok) { throw new Error('通知の作成に失敗しました。'); }
    return response.json();
  },
};

// --- 認証フローのコンポーネント ---
function AuthPage({ onLoginSuccess }) {
  const [mode, setMode] = useState('login'); // 'login', 'register', 'verify'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRegister = async (e) => { e.preventDefault(); setError(''); setLoading(true); try { await apiClient.register(name, email, password); setMode('verify'); } catch (err) { setError(err.message); } finally { setLoading(false); } };
  const handleVerify = async (e) => { e.preventDefault(); setError(''); setLoading(true); try { const data = await apiClient.verifyUser(email, code); onLoginSuccess(data.access_token); } catch (err) { setError(err.message); } finally { setLoading(false); } };
  const handleLogin = async (e) => { e.preventDefault(); setError(''); setLoading(true); try { const data = await apiClient.login(email, password); onLoginSuccess(data.access_token); } catch (err) { setError(err.message); } finally { setLoading(false); } };

  const renderContent = () => {
    switch (mode) {
      case 'verify':
        return (
          <>
            <div className="text-center">
              <h2 className="text-3xl font-bold text-white">認証コードを入力</h2>
              <p className="mt-2 text-gray-400">{email} に送信された6桁のコードを入力してください。</p>
            </div>
            <form onSubmit={handleVerify} className="mt-8 space-y-6">
              <input type="text" value={code} onChange={(e) => setCode(e.target.value)} placeholder="------" maxLength="6" className="w-full text-center text-2xl tracking-[1rem] px-4 py-3 bg-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
              <button type="submit" disabled={loading} className="w-full py-3 font-semibold text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
                {loading ? '検証中...' : '検証してログイン'}
              </button>
            </form>
            <p className="text-sm text-center text-gray-400">
                <button onClick={() => { setMode('register'); setError('')}} className="font-semibold text-indigo-400 hover:text-indigo-300">
                    登録画面に戻る
                </button>
            </p>
          </>
        );
      case 'register':
        return (
            <>
                <div className="text-center">
                    <h2 className="text-4xl font-extrabold text-white">アカウント作成</h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleRegister}>
                    <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="名前" required className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="メールアドレス" required className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="パスワード" required className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
                    <button type="submit" disabled={loading} className="w-full py-3 font-semibold text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
                        {loading ? '登録中...' : '登録'}
                    </button>
                </form>
                <p className="text-sm text-center text-gray-400">
                    すでにアカウントをお持ちですか？
                    <button onClick={() => { setMode('login'); setError('')}} className="ml-2 font-semibold text-indigo-400 hover:text-indigo-300">
                        ログイン
                    </button>
                </p>
            </>
        );
      default: // login
        return (
            <>
                <div className="text-center">
                    <h2 className="text-4xl font-extrabold text-white">Snoopへようこそ</h2>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleLogin}>
                    <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="メールアドレス" required className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
                    <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="パスワード" required className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"/>
                     <button type="submit" disabled={loading} className="w-full py-3 font-semibold text-white bg-indigo-600 rounded-md hover:bg-indigo-700">
                        {loading ? 'ログイン中...' : 'ログイン'}
                    </button>
                </form>
                <p className="text-sm text-center text-gray-400">
                    アカウントをお持ちでないですか？
                    <button onClick={() => { setMode('register'); setError('')}} className="ml-2 font-semibold text-indigo-400 hover:text-indigo-300">
                        登録
                    </button>
                </p>
            </>
        );
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">
      <div className="w-full max-w-md p-8 space-y-8 bg-gray-800 rounded-lg shadow-lg">
        {error && <p className="text-red-400 text-sm text-center mb-4 p-3 bg-red-900/50 rounded-md">{error}</p>}
        {renderContent()}
      </div>
    </div>
  );
}


// --- メインアプリケーションコンポーネント ---
function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

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
          localStorage.removeItem('habit-tracker-token');
          setToken(null);
          setUser(null);
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
    return <AuthPage onLoginSuccess={handleLoginSuccess} />;
  }

  return <HomePage user={user} token={token} onLogout={handleLogout} />;
}

// --- ホームページコンポーネント ---
function HomePage({ user, token, onLogout }) {
  const [page, setPage] = useState('dashboard'); // 'dashboard' or 'detail'
  const [selectedHabit, setSelectedHabit] = useState(null);

  const navigateToDetail = (habit) => {
      setSelectedHabit(habit);
      setPage('detail');
  };
  const navigateToDashboard = () => {
      setSelectedHabit(null);
      setPage('dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white font-sans">
      <Header user={user} onLogout={onLogout} />
      <main className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        {page === 'dashboard' && <Dashboard token={token} onHabitSelect={navigateToDetail} />}
        {page === 'detail' && selectedHabit && <HabitDetailPage habit={selectedHabit} token={token} onBack={navigateToDashboard} onHabitUpdated={navigateToDashboard} />}
      </main>
    </div>
  );
}

// --- ヘッダーコンポーネント ---
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

// --- ダッシュボードコンポーネント ---
function Dashboard({ token, onHabitSelect }) {
  const [habits, setHabits] = useState([]);
  const [isLoadingHabits, setIsLoadingHabits] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchHabits = useCallback(async () => {
    setIsLoadingHabits(true);
    try {
      const habitsData = await apiClient.getHabits(token);
      setHabits(habitsData);
    } catch (error) {
      console.error("Failed to fetch habits:", error);
    } finally {
      setIsLoadingHabits(false);
    }
  }, [token]);

  useEffect(() => {
    fetchHabits();
  }, [fetchHabits]);

  const handleHabitCreated = () => {
      fetchHabits();
      setIsModalOpen(false);
  };

  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold tracking-tight">ダッシュボード</h2>
        <button onClick={() => setIsModalOpen(true)} className="flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-white font-semibold transition-colors">
          <PlusCircle className="h-5 w-5 mr-2" /> 新しい習慣
        </button>
      </div>
      {isLoadingHabits ? ( <p>習慣を読み込み中...</p> ) : 
       habits.length === 0 ? ( <div className="text-center py-12 bg-gray-800 rounded-lg"><p className="text-gray-400">まだ習慣が登録されていません。</p></div> ) : 
      (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {habits.map(habit => (
            <HabitProgressCard key={habit.id} habit={habit} token={token} onSelect={() => onHabitSelect(habit)} />
          ))}
        </div>
      )}
      {isModalOpen && <AddHabitModal token={token} onClose={() => setIsModalOpen(false)} onHabitCreated={handleHabitCreated} />}
    </>
  );
}

// --- 習慣プログレスカードコンポーネント ---
function HabitProgressCard({ habit, token, onSelect }) {
  const [progress, setProgress] = useState({ completed: 0, total: 31 });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchJanuaryProgress = async () => {
      setIsLoading(true);
      const year = new Date().getFullYear();
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
    <div onClick={onSelect} className="bg-gray-800 p-6 rounded-lg transition-all duration-200 hover:bg-gray-700/80 cursor-pointer transform hover:scale-105">
        <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white">{habit.name}</h3>
            <TrendingUp className="h-6 w-6 text-gray-500"/>
        </div>
        <p className="text-gray-400 mt-2 text-sm h-10">{habit.description || '詳細がありません'}</p>
        <div className="mt-4">
            <div className="flex justify-between items-center text-sm mb-1">
                <span className="font-semibold text-indigo-400">1月の進捗</span>
                {isLoading ? <span className="text-gray-500">...</span> : <span className="text-white font-bold">{progress.completed} / {progress.total} 日</span>}
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2.5">
                <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${percentage}%`, transition: 'width 0.5s ease-in-out' }}></div>
            </div>
        </div>
    </div>
  );
}

// --- 習慣詳細/編集ページコンポーネント ---
function HabitDetailPage({ habit, token, onBack, onHabitUpdated }) {
    const [name, setName] = useState(habit.name);
    const [description, setDescription] = useState(habit.description || '');
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleUpdate = async (e) => {
        e.preventDefault(); setLoading(true); setError(''); setMessage('');
        try {
            await apiClient.updateHabit(token, habit.id, name, description);
            setMessage('習慣を更新しました！');
            setTimeout(() => {
                setMessage('');
                onHabitUpdated();
            }, 1500);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };
    
    const handleDelete = async () => {
        setLoading(true); setError('');
        try {
            await apiClient.deleteHabit(token, habit.id);
            onBack(); 
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
            setIsDeleting(false);
        }
    };

    return (
        <div>
            <button onClick={onBack} className="flex items-center text-indigo-400 hover:text-indigo-300 mb-6">
                <ChevronLeft className="h-5 w-5 mr-1" />
                ダッシュボードに戻る
            </button>

            <div className="bg-gray-800 rounded-lg p-6 md:p-8">
                <form onSubmit={handleUpdate}>
                    <div className="space-y-6">
                        <div>
                            <label htmlFor="habit-name" className="block text-sm font-medium text-gray-300 mb-1">習慣の名前</label>
                            <input id="habit-name" type="text" value={name} onChange={(e) => setName(e.target.value)} required className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <div>
                            <label htmlFor="habit-desc" className="block text-sm font-medium text-gray-300 mb-1">詳細（任意）</label>
                            <textarea id="habit-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows="3" className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        {error && <p className="text-red-400 text-sm">{error}</p>}
                        {message && <p className="text-green-400 text-sm">{message}</p>}
                    </div>

                    <div className="mt-8 flex flex-col sm:flex-row justify-between items-center gap-4">
                        <button type="button" onClick={() => setIsDeleting(true)} className="w-full sm:w-auto flex items-center justify-center px-4 py-2 bg-red-800 hover:bg-red-700 rounded-md text-white font-semibold transition-colors">
                            <Trash2 className="h-5 w-5 mr-2" /> 削除
                        </button>
                        <button type="submit" disabled={loading} className="w-full sm:w-auto flex items-center justify-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-white font-semibold transition-colors disabled:bg-indigo-400">
                           <Save className="h-5 w-5 mr-2" /> {loading ? '保存中...' : '変更を保存'}
                        </button>
                    </div>
                </form>
            </div>
            {isDeleting && (
                 <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
                    <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
                        <h3 className="text-xl font-bold">本当に削除しますか？</h3>
                        <p className="text-gray-400 mt-2">習慣「{habit.name}」を削除すると、元に戻すことはできません。</p>
                        <div className="flex justify-end space-x-4 mt-6">
                            <button onClick={() => setIsDeleting(false)} className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-md font-semibold">キャンセル</button>
                            <button onClick={handleDelete} disabled={loading} className="px-4 py-2 bg-red-600 hover:bg-red-500 rounded-md font-semibold disabled:bg-red-400">
                                {loading ? '削除中...' : '削除する'}
                            </button>
                        </div>
                    </div>
                 </div>
            )}
        </div>
    );
}

// --- 習慣追加モーダルコンポーネント ---
function AddHabitModal({ token, onClose, onHabitCreated }) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const [isAlarmEnabled, setIsAlarmEnabled] = useState(false);
    const [alarmTime, setAlarmTime] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault(); 
        if (isAlarmEnabled && !alarmTime) {
            setError('通知を有効にする場合は、時刻を設定してください。');
            return;
        }
        setLoading(true); 
        setError('');
        try {
            const newHabit = await apiClient.createHabit(token, name, description);
            
            if (isAlarmEnabled && alarmTime) {
                try {
                    await apiClient.createNotification(token, newHabit.id, alarmTime);
                } catch (notificationError) {
                    console.error('Notification creation failed:', notificationError);
                    alert(`習慣「${newHabit.name}」は作成されましたが、通知の設定に失敗しました。後で編集してください。`);
                }
            }
            
            onHabitCreated(newHabit);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }
    
    return (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4">
             <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg">
                <div className="p-6">
                    <h3 className="text-2xl font-bold mb-6">新しい習慣を作成</h3>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label htmlFor="habit-name" className="block text-sm font-medium text-gray-300 mb-1">習慣の名前</label>
                            <input id="habit-name" type="text" value={name} onChange={(e) => setName(e.target.value)} required className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                         <div>
                            <label htmlFor="habit-desc" className="block text-sm font-medium text-gray-300 mb-1">詳細（任意）</label>
                            <textarea id="habit-desc" value={description} onChange={(e) => setDescription(e.target.value)} rows="3" className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                        </div>
                        <hr className="border-gray-700" />
                        <div>
                            <label className="flex items-center space-x-3 cursor-pointer">
                                <input type="checkbox" checked={isAlarmEnabled} onChange={(e) => setIsAlarmEnabled(e.target.checked)} className="h-4 w-4 rounded bg-gray-700 border-gray-600 text-indigo-600 focus:ring-indigo-500" />
                                <div className="flex items-center text-gray-300">
                                  <Bell className="h-5 w-5 mr-2 text-gray-500" />
                                  <span>通知（アラーム）を有効にする</span>
                                </div>
                            </label>
                        </div>
                        {isAlarmEnabled && (
                            <div className="pl-8">
                                <label htmlFor="alarm-time" className="block text-sm font-medium text-gray-300 mb-1">通知時刻</label>
                                <input 
                                  id="alarm-time" 
                                  type="time" 
                                  value={alarmTime} 
                                  onChange={(e) => setAlarmTime(e.target.value)} 
                                  required={isAlarmEnabled} 
                                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                                  style={{ colorScheme: 'dark' }}
                                />
                            </div>
                        )}
                        {error && <p className="text-red-400 text-sm">{error}</p>}
                        <div className="flex justify-end space-x-4 pt-4">
                            <button type="button" onClick={onClose} className="px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-md font-semibold">キャンセル</button>
                            <button type="submit" disabled={loading} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md font-semibold disabled:bg-indigo-400">
                                {loading ? '作成中...' : '作成'}
                            </button>
                        </div>
                    </form>
                </div>
             </div>
        </div>
    );
}

export default App;
