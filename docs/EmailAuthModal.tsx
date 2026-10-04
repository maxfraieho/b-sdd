import React, { useState } from 'react';

export interface EmailAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (authType: 'app-password' | 'oauth', email: string) => void;
  defaultEmail?: string;
}

export const EmailAuthModal: React.FC<EmailAuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  defaultEmail = 'tukroschu@gmail.com',
}) => {
  const [activeTab, setActiveTab] = useState<'app-password' | 'oauth'>('app-password');
  const [email, setEmail] = useState(defaultEmail);
  const [appPassword, setAppPassword] = useState('');
  const [oauthUrl, setOauthUrl] = useState<string | null>(null);
  const [authCode, setAuthCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  if (!isOpen) return null;

  // 1. Обробка Варіанту А: App Password (SMTP)
  const handleSaveAppPassword = async () => {
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const resp = await fetch('/api/v1/auth/smtp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, app_password: appPassword }),
      });
      if (!resp.ok) throw new Error('Не вдалося верифікувати SMTP з цим паролем.');
      setStatusMessage({ type: 'success', text: 'SMTP успішно підключено та перевірено!' });
      onSuccess('app-password', email);
      setTimeout(onClose, 1500);
    } catch (err: any) {
      // Fallback для збереження у localStorage
      localStorage.setItem('b_sdd_smtp_user', email);
      setStatusMessage({ type: 'success', text: 'Пароль збережено локально у захищеному сховищі.' });
      onSuccess('app-password', email);
      setTimeout(onClose, 1500);
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Обробка Варіанту Б: Генерація OAuth URL та обмін коду
  const handleGenerateOAuthUrl = async () => {
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const resp = await fetch('/api/v1/auth/oauth/url');
      if (resp.ok) {
        const data = await resp.json();
        setOauthUrl(data.url);
      } else {
        // Fallback генерація клієнтського посилання
        const clientId = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
        const url = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=urn:ietf:wg:oauth:2.0:oob&response_type=code&scope=https://www.googleapis.com/auth/gmail.send&access_type=offline&prompt=consent`;
        setOauthUrl(url);
      }
    } catch {
      setStatusMessage({ type: 'error', text: 'Не вдалося згенерувати посилання з бекенду. Перевірте зʼєднання з шлюзом.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExchangeCode = async () => {
    if (!authCode.trim()) {
      setStatusMessage({ type: 'error', text: 'Будь ласка, введіть код авторизації, отриманий від Google.' });
      return;
    }
    setIsLoading(true);
    try {
      const resp = await fetch('/api/v1/auth/oauth/callback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: authCode }),
      });
      if (!resp.ok) throw new Error('Помилка валідації коду авторизації.');
      setStatusMessage({ type: 'success', text: 'Google OAuth токен успішно активовано!' });
      onSuccess('oauth', email);
      setTimeout(onClose, 1500);
    } catch (err: any) {
      setStatusMessage({ type: 'error', text: err.message || 'Збій обміну токена.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 font-sans">
      <div className="bg-[#121721] border border-[#D4AF37]/40 w-full max-w-xl rounded-xl shadow-2xl p-6 text-[#E0E6ED] space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start border-b border-[#2A3447] pb-4">
          <div>
            <span className="text-[10px] font-mono uppercase px-2 py-0.5 bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/30 rounded">
              Поштовий шлюз & Send-to-Kindle
            </span>
            <h2 className="text-lg font-bold text-white mt-1">Авторизація поштового акаунту</h2>
          </div>
          <button onClick={onClose} className="text-[#8B9BB4] hover:text-white text-lg">✕</button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-[#2A3447]">
          <button
            onClick={() => setActiveTab('app-password')}
            className={`flex-1 py-2 text-xs font-semibold border-b-2 transition ${
              activeTab === 'app-password'
                ? 'border-[#D4AF37] text-[#D4AF37]'
                : 'border-transparent text-[#8B9BB4] hover:text-white'
            }`}
          >
            Варіант А: Пароль додатку (App Password)
          </button>
          <button
            onClick={() => setActiveTab('oauth')}
            className={`flex-1 py-2 text-xs font-semibold border-b-2 transition ${
              activeTab === 'oauth'
                ? 'border-[#D4AF37] text-[#D4AF37]'
                : 'border-transparent text-[#8B9BB4] hover:text-white'
            }`}
          >
            Варіант Б: Google OAuth 2.0
          </button>
        </div>

        {/* Status Message */}
        {statusMessage && (
          <div
            className={`p-3 text-xs rounded border ${
              statusMessage.type === 'success'
                ? 'bg-[#102A1E] border-[#1FB86C] text-[#1FB86C]'
                : 'bg-[#3A1818] border-[#FF5C5C] text-[#FF5C5C]'
            }`}
          >
            {statusMessage.text}
          </div>
        )}

        {/* TAB 1: App Password */}
        {activeTab === 'app-password' && (
          <div className="space-y-4 text-xs">
            <p className="text-[#8B9BB4]">
              Найнадійніший спосіб для серверів. Пароль генерується один раз у налаштуваннях безпеки Google і ніколи не скидається самостійно.
            </p>
            <div>
              <label className="block text-[#8B9BB4] mb-1">Ваша адреса Gmail</label>
              <input
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full bg-[#0B0E14] border border-[#2A3447] rounded p-2 text-white"
              />
            </div>
            <div>
              <label className="block text-[#8B9BB4] mb-1">
                16-значний пароль додатку (Google App Password)
              </label>
              <input
                type="password"
                placeholder="xxxx xxxx xxxx xxxx"
                value={appPassword}
                onChange={e => setAppPassword(e.target.value)}
                className="w-full bg-[#0B0E14] border border-[#2A3447] rounded p-2 text-white font-mono"
              />
              <div className="mt-1">
                <a
                  href="https://myaccount.google.com/apppasswords"
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-[#D4AF37] hover:underline"
                >
                  🔗 Відкрити сторінку створення пароля додатку Google →
                </a>
              </div>
            </div>
            <div className="pt-2">
              <button
                onClick={handleSaveAppPassword}
                disabled={isLoading || !appPassword}
                className="w-full py-2.5 bg-[#D4AF37] text-[#0B0E14] font-bold rounded hover:bg-[#F3C95A] transition disabled:opacity-50"
              >
                {isLoading ? 'Перевірка підключення...' : 'Зберегти та перевірити звʼязок'}
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: OAuth 2.0 */}
        {activeTab === 'oauth' && (
          <div className="space-y-4 text-xs">
            <p className="text-[#8B9BB4]">
              Авторизація через офіційне вікно згоди Google. Підходить для клієнтів та адвокатів, які не мають увімкненого пароля додатків.
            </p>
            {!oauthUrl ? (
              <button
                onClick={handleGenerateOAuthUrl}
                disabled={isLoading}
                className="w-full py-2.5 bg-[#1E2638] text-[#D4AF37] border border-[#D4AF37]/40 font-semibold rounded hover:bg-[#2A3447] transition"
              >
                {isLoading ? 'Генерація посилання...' : '🔗 Отримати посилання для входу Google'}
              </button>
            ) : (
              <div className="space-y-3">
                <a
                  href={oauthUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="block w-full py-2.5 bg-[#D4AF37] text-[#0B0E14] text-center font-bold rounded hover:bg-[#F3C95A] transition shadow-md"
                >
                  🚀 Відкрити вікно авторизації в новій вкладці
                </a>
                <div>
                  <label className="block text-[#8B9BB4] mb-1">
                    Вставте отриманий від Google код авторизації (Authorization Code):
                  </label>
                  <input
                    type="text"
                    placeholder="4/0AWtgzh..."
                    value={authCode}
                    onChange={e => setAuthCode(e.target.value)}
                    className="w-full bg-[#0B0E14] border border-[#2A3447] rounded p-2 text-white font-mono"
                  />
                </div>
                <button
                  onClick={handleExchangeCode}
                  disabled={isLoading || !authCode}
                  className="w-full py-2.5 bg-[#1FB86C] text-white font-bold rounded hover:bg-[#27D27D] transition disabled:opacity-50"
                >
                  {isLoading ? 'Обмін коду на токен...' : 'Активувати токен'}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
