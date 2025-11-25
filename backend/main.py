from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from pydantic import BaseModel
import httpx
from bs4 import BeautifulSoup
import re
from typing import Dict
import math
import pandas as pd
from scipy.stats import pearsonr
import json
import requests

MAX_CONCURRENT_REQUESTS = 5
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
    
# Scraping
async def fetch_page(client: httpx.AsyncClient, username: str, page: int, semaphore: asyncio.Semaphore) -> dict:
    url = f"https://letterboxd.com/{username}/films/page/{page}/"
    print(f"Fetching: {url}")
    
    async with semaphore:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://letterboxd.com/" 
            }
            response = await client.get(url, headers=headers, timeout=15.0)
        except httpx.TimeoutException:
            print(f"Timeout on page {page}")
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
                    match = re.search(r"rated-([0-9]+)", rating_span["class"][-1])
                    rating = int(match.group(1)) / 2.0 if match else 0
                    
                films.append({"title": film_title, "slug": slug, "rating": rating})
    else:
        print("No posters found on this page.")
    return {"films": films, "total_pages": total_pages}
    
async def scrape_user(username: str) -> UserData:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with httpx.AsyncClient(headers=headers) as client:
        first_page_data = await fetch_page(client, username, 1, semaphore)
        
        films = first_page_data["films"]
        total_pages = first_page_data["total_pages"]
        
        if total_pages > 1:
            # Limit to 50 pages max to prevent infinite loops or massive waits
            limit = min(total_pages, 50) 
            tasks = [fetch_page(client, username, i, semaphore) for i in range(2, limit + 1)]
            
            # Run all remaining tasks
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

def scrape_poster(slug: str) -> str:
    url = f"https://letterboxd.com/film/{slug}/"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    script_w_data = soup.select_one('script[type="application/ld+json"]')
    if script_w_data:
        json_obj = json.loads(script_w_data.text.split(' */')[1].split('/* ]]>')[0])
        return json_obj['image']

    print(f"Poster not found for slug: {slug}\n{script_w_data}")
    return ""
    

# Compare
def calculate_similarity(u1: UserData, u2: UserData):
    # Jaccard Index
    shared_slugs = set(u1.ratings.keys()) & set(u2.ratings.keys())        
    union_slugs = set(u1.ratings.keys()) | set(u2.ratings.keys())
    jaccard = len(shared_slugs) / len(union_slugs) if union_slugs else 0
    
    # Pearson Correlation
    s1 = pd.Series(u1.ratings, name="u1")
    s2 = pd.Series(u2.ratings, name="u2")
    df = pd.concat([s1, s2], axis=1, join='inner')
    # Ignore unrated films
    df = df[(df['u1'] > 0) & (df['u2'] > 0)]
    
    shared_slugs = df.index.tolist()
    raw_pearson = 0.0 
    if len(df) >= 5:
        # Pearson returns (correlation, p-value). We just want correlation.
        # Handle case where variance is 0 (e.g. both users rated everything 5 stars)
        if df['u1'].std() == 0 or df['u2'].std() == 0:
             # If ratings are identical constants, perfect correlation (1.0)
             # If constants differ, undefined, but let's call it neutral (0.0)
            raw_pearson = 1.0 if df['u1'].mean() == df['u2'].mean() else 0.0
        else:
            raw_pearson, _ = pearsonr(df['u1'], df['u2'])
            
    # Normalize Pearson from [-1, 1] to [0, 1]
    normalized_taste = (raw_pearson + 1) / 2

    # Calculate disagreements
    df['diff'] = (df['u1'] - df['u2']).abs()
    sorted_df = df.sort_values('diff', ascending=False)
    top_diff = sorted_df.head(5)
    disagreements = []
    for slug, row in top_diff.iterrows():
        # Retrieve title from u1's details map
        title = u1.movie_details.get(slug, {}).get('title', slug)
        disagreements.append({
            "slug": slug,
            "title": title,
            "poster": scrape_poster(slug),
            "u1Rating": row['u1'],
            "u2Rating": row['u2'],
        })
    
    # agreements = []
    # bot_diff = sorted_df.tail(5)
    # for slug, row in bot_diff.iterrows():
    #     # Retrieve title from u1's details map
    #     title = u1.movie_details.get(slug, {}).get('title', slug)
    #     agreements.append({
    #         "slug": slug,
    #         "title": title,
    #         "poster": scrape_poster(slug),
    #         "u1Rating": row['u1'],
    #         "u2Rating": row['u2'],
    #     })
    
    final_score = (normalized_taste * 0.7) + (jaccard * 0.3)

    return {
        "users": [u1.username, u2.username],
        "metrics": {
            "finalScore": round(final_score * 100),
            "tasteMatch": round(normalized_taste * 100),
            "libraryOverlap": round(jaccard * 100),
            "sharedCount": len(shared_slugs),
            "totalWatched": [len(u1.ratings), len(u2.ratings)]
        },
        "controversialMovies": disagreements,
        # "agreeableMovies": agreements
    }

@app.post("/api/compare")
async def compare_users(request: CompareRequest):
    try:
        u1_data, u2_data = await asyncio.gather(
            scrape_user(request.user1),
            scrape_user(request.user2)
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Scraping failed. User might not exist or blocked.")
    
    if not u1_data.ratings or not u2_data.ratings:
        raise HTTPException(status_code=400, detail="Not enough data found.")

    return calculate_similarity(u1_data, u2_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)