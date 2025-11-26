# Letterboxd Neighbour
Measure film taste between two Letterboxd users.

Letterboxd Neighbour is a high-performance Python tool that identifies your _cinematic soulmates_. It calculates compatibility based on library overlap and rating similarity, powered by an async scraper with Semaphore concurrency control for fast execution.

## 📂File Structure
```
letterboxd-neighbour/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.css
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── lib/
│   │   │   └── utils.ts
│   │   └── types.ts
└── README.md
```

## 🚀Get Started
### Prerequisites
- **Python 3.10** or **3.11**
  - Adjust `requirements.txt` for older Python version
- **pip** (Python package installer).
- **pnpm**
  - Install with `npm install -g pnpm`
### Installation
1. Clone the repository
  ```bash
git clone https://github.com/michimochi25/letterboxd-neighbour.git
cd letterboxd-neighbour
```
2. Install backend dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```
3. Install frontend dependencies
```bash
cd frontend
pnpm install 
```
## 📖Usage
Run both backend and frontend. 
```bash
# Running backend
# Activate venv (if haven't already)
cd backend
source venv/bin/activate # On Windows use `venv\Scripts\activate`
uvicorn main:app --reload
```
```bash
# Running frontend
cd frontend
pnpm dev
```

## ⌛Coming Soon
- Deployment
- Shared genre

## License
This project is licensed under the MIT License - see the <a href="https://github.com/michimochi25/letterboxd-neighbour/blob/main/LICENSE">LICENSE<a> file for details.
