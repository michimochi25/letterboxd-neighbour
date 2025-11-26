# Letterboxd Neighbour
Measure film taste between two Letterboxd users.

Letterboxd Neighbour is a Python tool designed to help you discover "neighbours" on Letterboxd—users who share your movie taste, similar ratings, and watched films.

## File Structure
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

## Get Started
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
## Usage
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
