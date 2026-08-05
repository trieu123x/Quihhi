import { useState, useEffect, useRef } from 'react'
import questionsDataATBM from './questions.json'
import questionsDataHDH from './questions_hdh.json'
import './App.css'

// Audio Synthesis System using Web Audio API
const playSynthSound = (type, enabled) => {
  if (!enabled) return;
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    
    if (ctx.state === 'suspended') {
      ctx.resume();
    }

    if (type === 'click') {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(450, ctx.currentTime);
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
      osc.start();
      osc.stop(ctx.currentTime + 0.08);
    } else if (type === 'tick') {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(900, ctx.currentTime);
      gain.gain.setValueAtTime(0.04, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
      osc.start();
      osc.stop(ctx.currentTime + 0.04);
    } else if (type === 'correct') {
      const now = ctx.currentTime;
      const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.setValueAtTime(freq, now + idx * 0.07);
        gain.gain.setValueAtTime(0.12, now + idx * 0.07);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.07 + 0.25);
        osc.start(now + idx * 0.07);
        osc.stop(now + idx * 0.07 + 0.25);
      });
    } else if (type === 'incorrect') {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sawtooth';
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(160, now);
      osc.frequency.linearRampToValueAtTime(80, now + 0.35);
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.start();
      osc.stop(now + 0.35);
    } else if (type === 'streak') {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'triangle';
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.4);
      gain.gain.setValueAtTime(0.08, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      osc.start();
      osc.stop(now + 0.4);
    } else if (type === 'victory') {
      const now = ctx.currentTime;
      const chord = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99, 1046.50]; // C Major arpeggio
      chord.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.setValueAtTime(freq, now + idx * 0.09);
        gain.gain.setValueAtTime(0.1, now + idx * 0.09);
        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.09 + 0.35);
        osc.start(now + idx * 0.09);
        osc.stop(now + idx * 0.09 + 0.35);
      });
    }
  } catch (e) {
    console.error("Failed to play synth sound:", e);
  }
};

const BOT_NAMES = [
  "An_PTIT 🎓",
  "Ngọc_Đức_Lê 💻",
  "Hằng_KMA 🛡️",
  "Khánh_Bưu_Chính ⚡",
  "Vương_Cyber 🕵️",
  "Hacker_99 👾"
];

function App() {
  // Screen: 'subject', 'lobby', 'solo', 'flashcard', 'exam', 'results'
  const [screen, setScreen] = useState('subject');

  // Selected subject: 'atbm' | 'hdh'
  const [subject, setSubject] = useState(null);
  
  // Lobby settings
  const [playerName, setPlayerName] = useState(() => {
    return localStorage.getItem('atbm_player_name') || 'Triều Hỏi';
  });
  const [selectedChapters, setSelectedChapters] = useState([]);
  const [questionCount, setQuestionCount] = useState(20); // 10, 20, 50, all (0 = all)
  const [gameMode, setGameMode] = useState('solo'); // 'solo', 'flashcard', 'exam'
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [timerEnabled, setTimerEnabled] = useState(true);
  const [transitionDelay, setTransitionDelay] = useState('3');
  const [shortcutSet, setShortcutSet] = useState(() => {
    return localStorage.getItem('atbm_shortcut_set') || '1234';
  });

  useEffect(() => {
    localStorage.setItem('atbm_shortcut_set', shortcutSet);
  }, [shortcutSet]);

  // Active quiz states
  const [questions, setQuestions] = useState([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [streak, setStreak] = useState(0);
  const [maxStreak, setMaxStreak] = useState(0);
  const [userAnswers, setUserAnswers] = useState({}); // idx -> array of selected options
  const [correctCount, setCorrectCount] = useState(0);
  const [wrongCount, setWrongCount] = useState(0);
  
  // Feedback delay state
  const [showFeedback, setShowFeedback] = useState(false);
  const [isUserCorrect, setIsUserCorrect] = useState(false);
  const [selectedOptsInCurrentQ, setSelectedOptsInCurrentQ] = useState([]); // option texts user clicked for feedback mapping

  // Timer state for Solo Mode
  const [timeLeft, setTimeLeft] = useState(20);
  const timerIntervalRef = useRef(null);
  const feedbackTimeoutRef = useRef(null);
  
  // Leaderboard state
  const [leaderboard, setLeaderboard] = useState([]);

  // Flashcard states
  const [isFlipped, setIsFlipped] = useState(false);

  // Active dataset based on chosen subject
  const questionsData = subject === 'hdh' ? questionsDataHDH : questionsDataATBM;

  // Extract all unique chapters
  const allChapters = [...new Set(questionsData.map(q => q.chapter))].sort();

  // Save name changes
  useEffect(() => {
    localStorage.setItem('atbm_player_name', playerName);
  }, [playerName]);

  // Scroll to top on screen change
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [screen]);

  // Clean flash classes on unmount
  useEffect(() => {
    return () => {
      document.body.classList.remove('correct-flash', 'incorrect-flash');
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (feedbackTimeoutRef.current) clearTimeout(feedbackTimeoutRef.current);
    };
  }, []);

  const getChapterCount = (ch) => {
    return questionsData.filter(q => q.chapter === ch).length;
  };

  const toggleChapter = (ch) => {
    playSynthSound('click', audioEnabled);
    if (selectedChapters.includes(ch)) {
      setSelectedChapters(selectedChapters.filter(c => c !== ch));
    } else {
      setSelectedChapters([...selectedChapters, ch]);
    }
  };

  const selectAllChapters = () => {
    playSynthSound('click', audioEnabled);
    if (selectedChapters.length === allChapters.length) {
      setSelectedChapters([]);
    } else {
      setSelectedChapters([...allChapters]);
    }
  };

  const startQuiz = () => {
    playSynthSound('click', audioEnabled);
    document.body.classList.remove('correct-flash', 'incorrect-flash');
    
    let filtered = questionsData;
    if (selectedChapters.length > 0) {
      filtered = questionsData.filter(q => selectedChapters.includes(q.chapter));
    }

    let shuffled = [...filtered].sort(() => Math.random() - 0.5);

    if (questionCount > 0 && shuffled.length > questionCount) {
      shuffled = shuffled.slice(0, questionCount);
    }

    // Shuffle options for each question
    shuffled = shuffled.map(q => {
      const shuffledOptions = [...q.options].sort(() => Math.random() - 0.5);
      return { ...q, options: shuffledOptions };
    });

    setQuestions(shuffled);
    setCurrentIdx(0);
    setScore(0);
    setStreak(0);
    setMaxStreak(0);
    setUserAnswers({});
    setCorrectCount(0);
    setWrongCount(0);
    setIsFlipped(false);
    setShowFeedback(false);
    setSelectedOptsInCurrentQ([]);

    if (gameMode === 'solo') {
      const initialBots = BOT_NAMES.sort(() => Math.random() - 0.5)
        .slice(0, 4)
        .map(name => ({
          name,
          score: 0,
          streak: 0,
          accuracy: 0.6 + Math.random() * 0.3 // 60% to 90% accuracy
        }));
      
      const userEntry = { name: playerName + " (Bạn) 👤", score: 0, streak: 0, isUser: true };
      setLeaderboard([...initialBots, userEntry].sort((a, b) => b.score - a.score));
      setScreen('solo');
      initQuestionTimer();
    } else if (gameMode === 'flashcard') {
      setScreen('flashcard');
    } else {
      setScreen('exam');
    }
  };

  const initQuestionTimer = () => {
    setTimeLeft(20);
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    if (!timerEnabled) return;
    
    timerIntervalRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerIntervalRef.current);
          handleTimeOut();
          return 0;
        }
        if (prev <= 6) {
          playSynthSound('tick', audioEnabled);
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleTimeOut = () => {
    submitSoloAnswer([]); // Empty array represents timeout
  };

  const advanceToNextQuestion = () => {
    if (feedbackTimeoutRef.current) clearTimeout(feedbackTimeoutRef.current);
    setShowFeedback(false);
    setSelectedOptsInCurrentQ([]);

    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(prev => prev + 1);
      initQuestionTimer();
    } else {
      // Game complete!
      playSynthSound('victory', audioEnabled);
      setScreen('results');
    }
  };

  // Main Answer Submission Logic (Instant Feedback + 3s Auto-transition)
  const submitSoloAnswer = (selectedOpts) => {
    if (showFeedback) return;
    
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

    const currentQ = questions[currentIdx];
    const correctOptionsList = currentQ.options.filter(o => o.is_correct).map(o => o.text);
    
    // Check correctness
    let isCorrect = false;
    if (selectedOpts.length > 0) {
      const correctSelected = selectedOpts.filter(text => correctOptionsList.includes(text));
      const incorrectSelected = selectedOpts.filter(text => !correctOptionsList.includes(text));
      isCorrect = correctSelected.length === correctOptionsList.length && incorrectSelected.length === 0;
    }

    // Save state for showing feedback
    setIsUserCorrect(isCorrect);
    setSelectedOptsInCurrentQ(selectedOpts);
    setShowFeedback(true);

    // Save answer
    setUserAnswers(prev => ({ ...prev, [currentIdx]: selectedOpts }));

    // Score calculations
    let pointsEarned = 0;
    let newStreak = streak;
    if (isCorrect) {
      pointsEarned = 600 + (timerEnabled ? Math.round((timeLeft / 20) * 400) : 400);
      newStreak += 1;
      if (newStreak >= 3) {
        pointsEarned += Math.min(newStreak * 100, 500);
        playSynthSound('streak', audioEnabled);
      } else {
        playSynthSound('correct', audioEnabled);
      }
      setScore(prev => prev + pointsEarned);
      setStreak(newStreak);
      if (newStreak > maxStreak) setMaxStreak(newStreak);
      setCorrectCount(prev => prev + 1);
    } else {
      playSynthSound('incorrect', audioEnabled);
      newStreak = 0;
      setStreak(0);
      setWrongCount(prev => prev + 1);
    }

    // Simulate bots
    simulateBots(isCorrect ? pointsEarned : 0);

    // 3 seconds delay before automatically switching questions
    if (feedbackTimeoutRef.current) clearTimeout(feedbackTimeoutRef.current);
    feedbackTimeoutRef.current = setTimeout(() => {
      advanceToNextQuestion();
    }, (Math.max(0.5, parseFloat(transitionDelay) || 3)) * 1000);
  };

  // Handle Keyboard shortcuts in Solo mode
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (screen !== 'solo') return;

      if (showFeedback) {
        if (e.key === ' ') {
          e.preventDefault();
          advanceToNextQuestion();
        }
      } else {
        const optionKeys = shortcutSet === 'qwer' ? ['q', 'w', 'e', 'r'] : ['1', '2', '3', '4'];
        const pressedKey = e.key.toLowerCase();
        if (optionKeys.includes(pressedKey)) {
          e.preventDefault();
          const optIdx = optionKeys.indexOf(pressedKey);
          const currentQ = questions[currentIdx];
          if (currentQ && currentQ.options && currentQ.options[optIdx]) {
            playSynthSound('click', audioEnabled);
            submitSoloAnswer([currentQ.options[optIdx].text]);
          }
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [showFeedback, screen, currentIdx, questions, audioEnabled, submitSoloAnswer, advanceToNextQuestion, shortcutSet]);

  const simulateBots = (userPoints) => {
    setLeaderboard(prev => {
      const updated = prev.map(player => {
        if (player.isUser) {
          return { ...player, score: score + userPoints, streak: streak + (userPoints > 0 ? 1 : -streak) };
        }
        
        const isBotCorrect = Math.random() <= player.accuracy;
        let botPoints = 0;
        let botStreak = player.streak;
        
        if (isBotCorrect) {
          botStreak += 1;
          const botTimeLeft = 5 + Math.random() * 14; 
          botPoints = 600 + Math.round((botTimeLeft / 20) * 400);
          if (botStreak >= 3) {
            botPoints += Math.min(botStreak * 100, 500);
          }
        } else {
          botStreak = 0;
        }

        return {
          ...player,
          score: player.score + botPoints,
          streak: botStreak
        };
      });

      return updated.sort((a, b) => b.score - a.score);
    });
  };

  // Exam mode answer selection
  const handleExamAnswerSelect = (qIdx, optText) => {
    playSynthSound('click', audioEnabled);
    const currentQ = questions[qIdx];
    const isMultiSelect = currentQ.options.filter(o => o.is_correct).length > 1;
    const currentSelected = userAnswers[qIdx] || [];

    let newSelected;
    if (isMultiSelect) {
      if (currentSelected.includes(optText)) {
        newSelected = currentSelected.filter(t => t !== optText);
      } else {
        newSelected = [...currentSelected, optText];
      }
    } else {
      newSelected = [optText];
    }

    setUserAnswers(prev => ({ ...prev, [qIdx]: newSelected }));
  };

  const submitExam = () => {
    playSynthSound('victory', audioEnabled);
    
    let corrects = 0;
    let wrongs = 0;
    
    questions.forEach((q, idx) => {
      const correctList = q.options.filter(o => o.is_correct).map(o => o.text);
      const userList = userAnswers[idx] || [];
      
      const correctSelected = userList.filter(t => correctList.includes(t));
      const incorrectSelected = userList.filter(t => !correctList.includes(t));
      
      if (correctSelected.length === correctList.length && incorrectSelected.length === 0) {
        corrects += 1;
      } else {
        wrongs += 1;
      }
    });

    setCorrectCount(corrects);
    setWrongCount(wrongs);
    setScore(corrects * 10);
    setScreen('results');
  };

  // Flashcards handlers
  const prevCard = () => {
    playSynthSound('click', audioEnabled);
    setIsFlipped(false);
    if (currentIdx > 0) {
      setCurrentIdx(prev => prev - 1);
    }
  };

  const nextCard = () => {
    playSynthSound('click', audioEnabled);
    setIsFlipped(false);
    if (currentIdx + 1 < questions.length) {
      setCurrentIdx(prev => prev + 1);
    }
  };

  const handleCardFlip = () => {
    playSynthSound('click', audioEnabled);
    setIsFlipped(!isFlipped);
  };

  const exitToLobby = () => {
    playSynthSound('click', audioEnabled);
    document.body.classList.remove('correct-flash', 'incorrect-flash');
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    if (feedbackTimeoutRef.current) clearTimeout(feedbackTimeoutRef.current);
    setScreen('lobby');
  };

  const exitToSubject = () => {
    playSynthSound('click', audioEnabled);
    document.body.classList.remove('correct-flash', 'incorrect-flash');
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    if (feedbackTimeoutRef.current) clearTimeout(feedbackTimeoutRef.current);
    setSubject(null);
    setSelectedChapters([]);
    setScreen('subject');
  };

  // Helper values
  const currentQuestion = questions[currentIdx];
  const totalQuestionsCount = questions.length;
  const isCurrentQMultiSelect = currentQuestion?.options.filter(o => o.is_correct).length > 1;

  return (
    <>
      {/* Audio controls */}
      <button 
        className="audio-toggle" 
        onClick={() => setAudioEnabled(!audioEnabled)}
        title={audioEnabled ? "Tắt âm thanh" : "Bật âm thanh"}
      >
        {audioEnabled ? "🔊" : "🔇"}
      </button>

      {/* SUBJECT SELECTION SCREEN */}
      {screen === 'subject' && (
        <div className="subject-select-container">
          <div className="subject-hero">
            <h1 className="subject-hero-title">🎓 QUIHHI QUIZ</h1>
            <p className="subject-hero-sub">Chọn môn học để bắt đầu ôn tập</p>
          </div>

          <div className="subject-cards-row">
            {/* ATBM Card */}
            <div
              className="subject-card subject-card-atbm"
              onClick={() => {
                playSynthSound('click', audioEnabled);
                setSubject('atbm');
                setSelectedChapters([]);
                setScreen('lobby');
              }}
            >
              <div className="subject-card-icon">🛡️</div>
              <div className="subject-card-name">An Toàn Bảo Mật</div>
              <div className="subject-card-desc">Cơ sở An toàn thông tin</div>
              <div className="subject-card-meta">5 Chương · {questionsDataATBM.length} câu hỏi</div>
              <div className="subject-card-btn">Học Ngay →</div>
            </div>

            {/* HDH Card */}
            <div
              className="subject-card subject-card-hdh"
              onClick={() => {
                playSynthSound('click', audioEnabled);
                setSubject('hdh');
                setSelectedChapters([]);
                setScreen('lobby');
              }}
            >
              <div className="subject-card-icon">⚙️</div>
              <div className="subject-card-name">Hệ Điều Hành</div>
              <div className="subject-card-desc">ĐH Nguyễn Tất Thành</div>
              <div className="subject-card-meta">8 Chương · {questionsDataHDH.length} câu hỏi</div>
              <div className="subject-card-btn">Học Ngay →</div>
            </div>
          </div>
        </div>
      )}

      {/* LOBBY SCREEN */}
      {screen === 'lobby' && (
        <div className="lobby-container">
          <div className="logo-section">
            <button
              onClick={exitToSubject}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-glass)',
                color: 'var(--text-gray)',
                borderRadius: '8px',
                padding: '6px 14px',
                cursor: 'pointer',
                fontSize: '0.85rem',
                marginBottom: '12px',
                display: 'inline-block'
              }}
            >
              ← Đổi môn học
            </button>
            <h1 className="logo-title">
              {subject === 'hdh' ? '⚙️ HỆ ĐIỀU HÀNH' : '🛡️ AN TOÀN BẢO MẬT'}
            </h1>
            <p style={{color: 'var(--text-gray)', fontSize: '1.1rem', marginTop: '10px'}}>
              {subject === 'hdh'
                ? 'Ngân hàng câu hỏi Hệ điều hành · ĐH Nguyễn Tất Thành'
                : 'Ôn thi trắc nghiệm Cơ sở An toàn thông tin (5 Chương học)'}
            </p>
          </div>

          <div className="lobby-card glass-panel" style={{width: '100%'}}>
            <div className="input-group">
              <label className="input-label" htmlFor="player-name-input">Tên Người Chơi:</label>
              <input 
                id="player-name-input"
                type="text" 
                className="cyber-input" 
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Nhập tên của bạn..."
              />
            </div>

            <div className="input-group">
              <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}>
                <label className="input-label">Chọn Chương Học (Có {allChapters.length} chương):</label>
                <button 
                  onClick={selectAllChapters}
                  style={{
                    background: 'transparent', 
                    border: 'none', 
                    color: 'var(--secondary)', 
                    cursor: 'pointer',
                    fontWeight: 600,
                    fontSize: '0.85rem'
                  }}
                >
                  {selectedChapters.length === allChapters.length ? "Bỏ chọn tất cả" : "Chọn tất cả"}
                </button>
              </div>
              
              <div className="chapters-grid">
                {allChapters.map((ch, idx) => {
                  const isSelected = selectedChapters.includes(ch);
                  return (
                    <div 
                      key={idx}
                      className={`chapter-card ${isSelected ? 'selected' : ''}`}
                      onClick={() => toggleChapter(ch)}
                    >
                      <span className="chapter-name">{ch.replace(':', '')}</span>
                      <span className="chapter-count">{getChapterCount(ch)} câu</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="options-flex">
              <div className="input-group">
                <label className="input-label">Số Lượng Câu Hỏi:</label>
                <div className="segmented-control">
                  {[10, 20, 50, 0].map((count) => (
                    <button
                      key={count}
                      className={`segment-btn ${questionCount === count ? 'active' : ''}`}
                      onClick={() => {
                        playSynthSound('click', audioEnabled);
                        setQuestionCount(count);
                      }}
                    >
                      {count === 0 ? "Tất cả" : count}
                    </button>
                  ))}
                </div>
              </div>

              <div className="input-group">
                <label className="input-label">Chế Độ Chơi:</label>
                <div className="segmented-control">
                  {[
                    { id: 'solo', label: 'Lớp Học (Solo)' },
                    { id: 'flashcard', label: 'Flashcards' },
                    { id: 'exam', label: 'Thi Thử' }
                  ].map((mode) => (
                    <button
                      key={mode.id}
                      className={`segment-btn ${gameMode === mode.id ? 'active' : ''}`}
                      onClick={() => {
                        playSynthSound('click', audioEnabled);
                        setGameMode(mode.id);
                      }}
                    >
                      {mode.label}
                    </button>
                  ))}
                </div>
                <div className="mode-description">
                  {gameMode === 'solo' && `🔥 Đua top thời gian thực, có âm thanh vui nhộn & đáp án tự động chuyển câu sau ${Math.max(0.5, parseFloat(transitionDelay) || 3)}s!`}
                  {gameMode === 'flashcard' && "📖 Học nhanh. Lật thẻ xem đáp án, phù hợp để ôn lại bài trước giờ thi."}
                  {gameMode === 'exam' && "📝 Làm bài thi thử 5 chương không giới hạn thời gian. Nộp bài để xem điểm số."}
                </div>
              </div>
            </div>
            
            <div className="options-flex" style={{marginBottom: '15px'}}>
              <div className="input-group" style={{display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '10px'}}>
                <input 
                  type="checkbox" 
                  id="timer-enable-chk" 
                  checked={timerEnabled} 
                  onChange={(e) => {
                    playSynthSound('click', audioEnabled);
                    setTimerEnabled(e.target.checked);
                  }}
                  style={{width: '20px', height: '20px', cursor: 'pointer'}}
                />
                <label htmlFor="timer-enable-chk" style={{cursor: 'pointer', fontWeight: 600, fontSize: '0.95rem'}}>
                  Giới hạn thời gian (20s)
                </label>
              </div>

              <div className="input-group" style={{display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '10px'}}>
                <label htmlFor="delay-input" style={{fontWeight: 600, fontSize: '0.95rem', whiteSpace: 'nowrap'}}>
                  Chuyển câu sau (giây) or nhấn space:
                </label>
                <input 
                  id="delay-input"
                  type="number" 
                  min="0.5"
                  step="0.5"
                  max="10" 
                  className="cyber-input" 
                  style={{width: '80px', padding: '6px', textAlign: 'center', border: '1px solid var(--border-glass)', borderRadius: '8px'}}
                  value={transitionDelay}
                  onChange={(e) => setTransitionDelay(e.target.value)}
                />
              </div>
            </div>

            <div className="options-flex" style={{marginBottom: '15px'}}>
              <div className="input-group" style={{display: 'flex', flexDirection: 'row', alignItems: 'center', gap: '10px'}}>
                <label htmlFor="shortcut-select" style={{fontWeight: 600, fontSize: '0.95rem', whiteSpace: 'nowrap'}}>
                  Phím Chọn Đáp Án:
                </label>
                <select
                  id="shortcut-select"
                  className="cyber-input"
                  style={{
                    padding: '8px 12px',
                    border: '1px solid var(--border-glass)',
                    borderRadius: '8px',
                    background: 'rgba(0, 0, 0, 0.4)',
                    color: 'var(--text-white)',
                    fontFamily: 'var(--font-family)',
                    fontSize: '0.95rem',
                    cursor: 'pointer',
                    outline: 'none'
                  }}
                  value={shortcutSet}
                  onChange={(e) => {
                    playSynthSound('click', audioEnabled);
                    setShortcutSet(e.target.value);
                  }}
                >
                  <option value="1234">Phím số (1, 2, 3, 4)</option>
                  <option value="qwer">Phím chữ (Q, W, E, R)</option>
                </select>
              </div>
            </div>

            <div style={{display: 'flex', justifyContent: 'center', marginTop: '10px'}}>
              <button className="btn-cyber" onClick={startQuiz} style={{width: '240px'}}>
                Bắt Đầu Chơi
              </button>
            </div>
          </div>
        </div>
      )}

      {/* SOLO GAME SCREEN */}
      {screen === 'solo' && currentQuestion && (
        <div style={{display: 'flex', flexDirection: 'column', minHeight: '100vh'}}>
          {/* Header section matching Quizizz header layout */}
          <div className="top-header-bar">
            <div className="top-left-status">
              <div className="streak-pill has-streak">
                ⚡ {score} pts
              </div>
              <div className="streak-pill">
                🔥 {streak}
              </div>
              <div className="level-badge">Thường</div>
            </div>
            <div className="top-right-controls">
              <button className="control-icon-btn" onClick={exitToLobby} title="Về sảnh chính">☰</button>
              <button className="control-icon-btn" onClick={() => {
                if (!document.fullscreenElement) {
                  document.documentElement.requestFullscreen().catch(() => {});
                } else {
                  document.exitFullscreen();
                }
              }}>⛶</button>
            </div>
          </div>

          {timerEnabled && (
            <div className="play-timer-container">
              <div 
                className="play-timer-bar" 
                style={{ width: `${(timeLeft / 20) * 100}%`, backgroundColor: showFeedback ? 'transparent' : 'var(--secondary)' }}
              ></div>
            </div>
          )}

          {/* Play Field Area */}
          <div className="play-field-container">
            {/* Center question box */}
            <div className="quiz-question-box">
              <div className="quiz-progress-badge">
                {currentIdx + 1} / {totalQuestionsCount}
              </div>
              <h2 className="quiz-question-text">{currentQuestion.question}</h2>
            </div>

            {/* Answer Cards Row */}
            <div className="quiz-options-row">
              {currentQuestion.options.map((opt, oIdx) => {
                const isCorrect = opt.is_correct;
                const isSelected = selectedOptsInCurrentQ.includes(opt.text);

                // Feedback rendering rules using visibility instead of DOM removal to prevent resizing
                const isHidden = showFeedback && (
                  isUserCorrect 
                    ? !isCorrect 
                    : (!isCorrect && !isSelected)
                );

                let stateClass = '';
                if (showFeedback) {
                  if (isCorrect) {
                    stateClass = 'card-correct';
                  } else if (isSelected) {
                    stateClass = 'card-incorrect';
                  }
                }

                return (
                  <button
                    key={oIdx}
                    className={`quiz-option-card ${stateClass}`}
                    style={{ visibility: isHidden ? 'hidden' : 'visible' }}
                    onClick={() => {
                      if (!showFeedback) {
                        playSynthSound('click', audioEnabled);
                        submitSoloAnswer([opt.text]);
                      }
                    }}
                    disabled={showFeedback}
                  >
                    <span className="shortcut-badge">
                      {shortcutSet === 'qwer' ? ['Q', 'W', 'E', 'R'][oIdx] : ['1', '2', '3', '4'][oIdx]}
                    </span>
                    <span>{opt.text}</span>
                  </button>
                );
              })}
            </div>
          </div>

        </div>
      )}

      {/* FLASHCARD MODE SCREEN */}
      {screen === 'flashcard' && currentQuestion && (
        <div className="flashcards-container">
          <div style={{display: 'flex', width: '100%', justifyContent: 'space-between', alignItems: 'center'}}>
            <button className="btn-cyber secondary-btn" onClick={exitToLobby} style={{padding: '8px 16px', fontSize: '0.9rem'}}>
              ⬅ Về trang chủ
            </button>
            <div className="flashcard-index">Thẻ {currentIdx + 1} / {totalQuestionsCount}</div>
          </div>

          <div 
            className={`flashcard-wrapper ${isFlipped ? 'flipped' : ''}`}
            onClick={handleCardFlip}
          >
            <div className="flashcard-inner">
              <div className="card-front">
                <span className="card-type">{currentQuestion.chapter} - Câu {currentIdx + 1}</span>
                <p className="card-question-text">{currentQuestion.question}</p>
                <div className="card-hint">Nhấp vào thẻ để xem đáp án 🔄</div>
              </div>
              <div className="card-back">
                <span className="card-answer-label">Đáp Án Đúng:</span>
                <div className="card-answer-text">
                  {currentQuestion.options.filter(o => o.is_correct).map((o, idx) => (
                    <div key={idx} style={{marginTop: '10px', padding: '10px', background: 'rgba(255,255,255,0.08)', borderRadius: '10px'}}>
                      ✅ {o.text}
                    </div>
                  ))}
                </div>
                <div className="card-hint">Nhấp vào thẻ để xem câu hỏi 🔄</div>
              </div>
            </div>
          </div>

          <div className="flashcards-controls">
            <button 
              className="round-btn" 
              onClick={prevCard} 
              disabled={currentIdx === 0}
            >
              ◀
            </button>
            <button 
              className="btn-cyber" 
              onClick={handleCardFlip} 
              style={{padding: '10px 20px', fontSize: '0.95rem'}}
            >
              Lật Thẻ 🔄
            </button>
            <button 
              className="round-btn" 
              onClick={nextCard} 
              disabled={currentIdx === totalQuestionsCount - 1}
            >
              ▶
            </button>
          </div>
        </div>
      )}

      {/* EXAM SCREEN */}
      {screen === 'exam' && (
        <div className="exam-container">
          <div className="exam-header glass-panel">
            <div>
              <h2 className="exam-title">
                {subject === 'hdh' ? 'Bài Thi Thử Hệ Điều Hành' : 'Bài Thi Thử An Toàn Thông Tin'}
              </h2>
              <p style={{color: 'var(--text-gray)', fontSize: '0.9rem', marginTop: '4px'}}>
                Chế độ thi thử • Tổng số: {totalQuestionsCount} câu hỏi
              </p>
            </div>
            <div className="exam-meta">
              Đã trả lời: {Object.keys(userAnswers).length} / {totalQuestionsCount}
            </div>
          </div>

          <div className="exam-list">
            {questions.map((q, qIdx) => {
              const qSelected = userAnswers[qIdx] || [];
              const isMulti = q.options.filter(o => o.is_correct).length > 1;
              
              return (
                <div key={qIdx} className="exam-question-item glass-panel">
                  <div className="exam-question-num">Câu {qIdx + 1} ({q.chapter}) {isMulti ? "(Chọn nhiều)" : ""}</div>
                  <h3 className="exam-question-title">{q.question}</h3>
                  <div className="exam-options-list">
                    {q.options.map((opt, oIdx) => {
                      const isSelected = qSelected.includes(opt.text);
                      const prefixChar = String.fromCharCode(65 + oIdx);
                      
                      return (
                        <div 
                          key={oIdx}
                          className={`exam-option-item ${isSelected ? 'selected' : ''}`}
                          onClick={() => handleExamAnswerSelect(qIdx, opt.text)}
                        >
                          <div className="exam-option-checkbox">
                            {isSelected ? (isMulti ? "✓" : "●") : ""}
                          </div>
                          <span><strong>{prefixChar}.</strong> {opt.text}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="exam-submit-section">
            <button className="btn-cyber" onClick={submitExam} style={{width: '280px'}}>
              Nộp Bài Thi
            </button>
          </div>
        </div>
      )}

      {/* RESULT SCREEN */}
      {screen === 'results' && (
        <div className="results-container">
          <div className="results-header-card glass-panel">
            {gameMode === 'solo' && (
              <div className="results-rank">
                🏆 Hạng #{leaderboard.findIndex(p => p.isUser) + 1} / {leaderboard.length}
              </div>
            )}
            <h2 className="results-score-title">Kết Quả Chung Cuộc</h2>
            <div className="results-score-value">
              {gameMode === 'solo' ? `${score} pts` : `${correctCount}/${totalQuestionsCount}`}
            </div>

            <div className="results-stats-row">
              <div className="results-stat-box">
                <span className="results-stat-num correct-val">{correctCount}</span>
                <span className="results-stat-label">Chính xác</span>
              </div>
              <div className="results-stat-box">
                <span className="results-stat-num incorrect-val">{wrongCount}</span>
                <span className="results-stat-label">Sai</span>
              </div>
              <div className="results-stat-box">
                <span className="results-stat-num accuracy-val">
                  {totalQuestionsCount > 0 ? Math.round((correctCount / totalQuestionsCount) * 100) : 0}%
                </span>
                <span className="results-stat-label">Tỉ lệ đúng</span>
              </div>
            </div>
            
            {gameMode === 'solo' && maxStreak >= 3 && (
              <div style={{color: 'var(--gold)', fontWeight: 'bold', marginTop: '10px'}}>
                🔥 Chuỗi liên tiếp cao nhất: {maxStreak} câu!
              </div>
            )}

            <div className="results-actions" style={{marginTop: '30px'}}>
              <button className="btn-cyber" onClick={startQuiz}>
                🔄 Chơi Lại
              </button>
              <button className="btn-cyber secondary-btn" onClick={exitToLobby}>
                🏠 Trang Chủ
              </button>
            </div>
          </div>

          {/* Detailed Question Review */}
          <div className="glass-panel">
            <h3 className="review-title">📋 Xem Lại Các Câu Hỏi</h3>
            <div className="review-list" style={{marginTop: '20px'}}>
              {questions.map((q, idx) => {
                const uSel = userAnswers[idx] || [];
                const correctList = q.options.filter(o => o.is_correct).map(o => o.text);
                
                const isCorrect = uSel.filter(t => correctList.includes(t)).length === correctList.length && 
                                  uSel.filter(t => !correctList.includes(t)).length === 0;

                return (
                  <div key={idx} className={`review-item glass-panel ${isCorrect ? 'correct-item' : 'incorrect-item'}`}>
                    <div className="review-q-num">Câu {idx + 1} ({q.chapter})</div>
                    <div className="review-q-text">{q.question}</div>
                    <div className="review-options">
                      {q.options.map((opt, oIdx) => {
                        const isOptCorrect = opt.is_correct;
                        const isOptUserSel = uSel.includes(opt.text);
                        
                        let optClass = '';
                        if (isOptCorrect) {
                          optClass = 'correct-opt';
                        } else if (isOptUserSel && !isOptCorrect) {
                          optClass = 'user-opt-wrong';
                        }

                        return (
                          <div key={oIdx} className={`review-opt ${optClass}`}>
                            {isOptCorrect ? "✅ " : isOptUserSel ? "❌ " : "◦ "}
                            {opt.text}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App
