# 🎓 Quihhi Quiz

Web app ôn thi trắc nghiệm cho 2 môn học, được xây dựng bằng **React + Vite**.

## 📚 Môn học

| Môn | Nguồn | Số câu |
|---|---|---|
| 🛡️ An Toàn Bảo Mật (CSATTT) | PTIT | ~1000+ câu |
| ⚙️ Hệ Điều Hành (HDH) | ĐH Nguyễn Tất Thành | 343 câu / 8 chương |

## ✨ Tính năng

- **Chọn môn học** ngay khi vào trang
- **3 chế độ chơi:** Lớp Học (Solo + Leaderboard), Flashcards, Thi Thử
- **Chọn chương** để ôn tập theo từng phần
- **Âm thanh** phản hồi đúng/sai, chuỗi combo
- **Bộ hẹn giờ** 20 giây mỗi câu (có thể tắt)
- **Phím tắt** 1/2/3/4 hoặc Q/W/E/R để chọn đáp án

## 🚀 Cài đặt & Chạy

```bash
npm install
npm run dev
```

## 📁 Cấu trúc

```
├── src/
│   ├── App.jsx           # Main app component
│   ├── App.css           # Styling
│   ├── questions.json    # Bộ câu hỏi ATBM
│   └── questions_hdh.json # Bộ câu hỏi HDH
├── parse_global.py       # Script parse PDF ATBM
├── parse_hdh.py          # Script parse PDF HDH
├── cau-hoi-on-tap-csattt-ptit.pdf
└── NganHangCauHoiHDH_DhNguyenTatThanh.pdf
```

## 🔧 Parse lại câu hỏi từ PDF

```bash
# Parse ATBM
python parse_global.py

# Parse HDH (đáp án được bôi vàng trong PDF)
python parse_hdh.py
```
