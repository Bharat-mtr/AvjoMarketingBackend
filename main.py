from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from together_ai import analyze_product_name
from meta_ad_library import search_meta_ads
from dotenv import load_dotenv 
from ad_analysis import analyze_ads, idea_from_ads
import os


load_dotenv()

app = FastAPI()

class AdAnalysisRequest(BaseModel):
    product_name: str
    company_name: str

class AdAnalysisResponse(BaseModel):
    keyword: str
    ads: dict

@app.post("/analyseMetaAds")
async def analyse_meta_ads(request: AdAnalysisRequest):
    try:
        ads_data = analyze_ads(request.product_name, request.company_name)

        ads_idea = idea_from_ads(ads_data, request.product_name)
        print("ad ideas are")
        print(ads_idea)

        return {"ads_idea": ads_idea}
    
        # # Analyze product name to get search keyword
        # keyword = analyze_product_name(request.product_name, request.company_name)

        # # Search Meta Ad Library API using the generated keyword
        # ads = search_meta_ads(keyword)

        #return AdAnalysisResponse(keyword=keyword, ads=ads)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
