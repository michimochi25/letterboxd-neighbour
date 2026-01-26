import asyncio
import json
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
import pandas as pd
from scipy.stats import pearsonr

from curl_cffi.requests import AsyncSession

MAX_CONCURRENT_REQUESTS = 3
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompareRequest(BaseModel):
    user1: str
    user2: str
    
class UserData(BaseModel):
    username: str
    ratings: Dict[str, float]
    movie_details: Dict[str, dict]

async def fetch_page(session: AsyncSession, username: str, page: int, semaphore: asyncio.Semaphore) -> dict:
    url = f"https://letterboxd.com/{username}/films/page/{page}/"
    print(f"Fetching: {url}")
    
    async with semaphore:
        try:
            response = await session.get(url, timeout=15.0)
        except Exception as e:
            print(f"Timeout or Error on page {page}: {e}")
            return {"films": [], "total_pages": 0}
        
    if response.status_code != 200:
        print(f"Failure: Status Code {response.status_code}")
        return {"films": [], "total_pages": 0}
    
    soup = BeautifulSoup(response.text, "html.parser")
    films = []
    total_pages = 0
    
    if page == 1:
        pagination = soup.select("div.pagination .paginate-pages li.paginate-page a")
        if pagination:
            try:
                last_page_text = pagination[-1].get_text(strip=True)
                total_pages = int(last_page_text)
            except ValueError:
                total_pages = 1
        else:
            total_pages = 1
    
    poster_containers = soup.select_one("div.poster-grid")
    if poster_containers:
        items = poster_containers.find_all("li")
        for li in items:
            film_div = li.find("div", class_="react-component")
            if film_div:
                film_title = film_div.get("data-item-name")
                slug = film_div.get("data-item-slug")
                
                # Get rating
                rating_span = li.find("span", class_="rating")
                rating: float = 0
                if rating_span:
                    # Class example: "rating rated-9" -> 9/2 = 4.5
                    classes = rating_span.get("class", [])
                    # Find the class that looks like rated-X
                    for cls in classes:
                        if cls.startswith("rated-"):
                            try:
                                rating_val = int(cls.split("-")[1])
                                rating = rating_val / 2.0
                            except (ValueError, IndexError):
                                pass
                            break
                    
                films.append({"title": film_title, "slug": slug, "rating": rating})
    return {"films": films, "total_pages": total_pages}

async def scrape_user(username: str) -> UserData:
    async with AsyncSession(impersonate="chrome120") as session:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        # Fetch page 1 to get total pages
        first_page_data = await fetch_page(session, username, 1, semaphore)
        
        films = first_page_data["films"]
        total_pages = first_page_data["total_pages"]
        
        if total_pages > 1:
            limit = min(total_pages, 50)
            tasks = [fetch_page(session, username, i, semaphore) for i in range(2, limit + 1)]
            
            results = await asyncio.gather(*tasks)
            
            for res in results:
                films.extend(res["films"])
                
        ratings_map = {}
        details_map = {}
        
        for film in films:
            ratings_map[film["slug"]] = film["rating"]
            details_map[film["slug"]] = {
                "title": film["title"],
                "rating": film["rating"],
            }
        
        return UserData(username=username, ratings=ratings_map, movie_details=details_map)

async def scrape_poster(session: AsyncSession, slug: str) -> str:
    """
    Scrapes the poster image URL asynchronously.
    """
    url = f"https://letterboxd.com/film/{slug}/"
    try:
        r = await session.get(url, timeout=10.0)
        if r.status_code != 200:
            return ""
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Original logic preserved, but safer
        script_w_data = soup.select_one('script[type="application/ld+json"]')
        if script_w_data:
            script_content = script_w_data.text
            # Simple check if CDATA exists
            if '*/' in script_content:
                script_content = script_content.split(' */')[1]
            if '/* ]]>' in script_content:
                script_content = script_content.split('/* ]]>')[0]
                
            json_obj = json.loads(script_content)
            return json_obj.get('image', "")
            
    except Exception as e:
        print(f"Error fetching poster for {slug}: {e}")
        
    return ""

async def calculate_similarity(u1: UserData, u2: UserData):
    # Jaccard Index
    shared_slugs = set(u1.ratings.keys()) & set(u2.ratings.keys())        
    union_slugs = set(u1.ratings.keys()) | set(u2.ratings.keys())
    jaccard = len(shared_slugs) / len(union_slugs) if union_slugs else 0
    
    # Pearson Correlation
    s1 = pd.Series(u1.ratings, name="u1")
    s2 = pd.Series(u2.ratings, name="u2")
    df = pd.concat([s1, s2], axis=1, join='inner')
    
    # Filter for movies both have seen
    df = df[(df['u1'] > 0) & (df['u2'] > 0)]
    
    # shared_slugs updated to intersection of rated movies
    shared_slugs_list = df.index.tolist()
    
    raw_pearson = 0.0 
    if len(df) >= 5:
        if df['u1'].std() == 0 or df['u2'].std() == 0:
            # If variance is 0 (all ratings identical), check if means match
            raw_pearson = 1.0 if df['u1'].mean() == df['u2'].mean() else 0.0
        else:
            raw_pearson, _ = pearsonr(df['u1'], df['u2'])
            
    normalized_taste = (raw_pearson + 1) / 2

    # Calculate disagreements
    df['diff'] = (df['u1'] - df['u2']).abs()
    sorted_df = df.sort_values('diff', ascending=False)
    top_diff = sorted_df.head(5)
    
    # --- ASYNC POSTER FETCHING ---
    # We create a temporary session to fetch all posters in parallel
    disagreements = []
    
    async with AsyncSession(impersonate="chrome120") as poster_session:
        poster_tasks = []
        rows_data = [] # Keep track of data to recombine with poster result
        
        for slug, row in top_diff.iterrows():
            rows_data.append((slug, row))
            poster_tasks.append(scrape_poster(poster_session, str(slug)))
            
        # Fire all requests at once
        poster_urls = await asyncio.gather(*poster_tasks)
        
        # Combine results
        for (slug, row), poster_url in zip(rows_data, poster_urls):
            title = u1.movie_details.get(slug, {}).get('title', slug)
            disagreements.append({
                "slug": slug,
                "title": title,
                "poster": poster_url,
                "u1Rating": row['u1'],
                "u2Rating": row['u2'],
            })

    final_score = (normalized_taste * 0.7) + (jaccard * 0.3)

    return {
        "users": [u1.username, u2.username],
        "metrics": {
            "finalScore": round(final_score * 100),
            "tasteMatch": round(normalized_taste * 100),
            "libraryOverlap": round(jaccard * 100),
            "sharedCount": len(shared_slugs_list),
            "totalWatched": [len(u1.ratings), len(u2.ratings)]
        },
        "controversialMovies": disagreements,
    }

@app.post("/api/compare")
async def compare_users(request: CompareRequest):
    try:
        # Fetch both users in parallel
        u1_data, u2_data = await asyncio.gather(
            scrape_user(request.user1),
            scrape_user(request.user2)
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Scraping failed. User might not exist or blocked.")
    
    if not u1_data.ratings or not u2_data.ratings:
        raise HTTPException(status_code=400, detail="Not enough data found.")

    # Await the calculation (since it now does async scraping for posters)
    return await calculate_similarity(u1_data, u2_data)

@app.get("/")
def read_root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)