import json
from together import Together
from pydantic import BaseModel, Field
from dotenv import load_dotenv 
import os
from enum import Enum
from typing import Literal


load_dotenv()

together = Together()

class AnalysisResult(BaseModel):
    keyword: str = Field(description="A keyword generated from the product name analysis.")

class RelevanceResponse(BaseModel):
    is_relevant: Literal["yes", "no"] = Field(
        description="Indicates whether the ad text is relevant to the keyword",
        examples=["yes", "no"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_relevant": "yes"
            }
        }

class AdvertisementIdea(BaseModel):
    idea_of_ad: str = Field(
        ...,
        min_length=200,
        max_length=400,
        description="Template-style advertising concept that can be adapted for different products"
    )

def analyze_text(prompt: str,schema,  model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo") -> str:
    """Generalized function to call Together AI with a prompt and return a JSON response."""
    extract = together.chat.completions.create(
        messages=[
            {"role": "system", "content": "Analyze the input text and respond in JSON format."},
            {"role": "user", "content": prompt},
        ],
        model=model,
        response_format={"type": "json_object", "schema": schema.model_json_schema()},
    )
    
    output = json.loads(extract.choices[0].message.content)
    return output

def analyze_text_image(prompt: str,image_url:str,  schema ,  model: str = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo") -> str:
    """Generalized function to call Together AI with a prompt and return a JSON response."""
    print(prompt, image_url, schema)
    extract = together.chat.completions.create(
        messages=[
            # {"role": "system", "content": "Analyze the input text and image and respond in JSON format."},
            {"role": "user", "content": [{"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                    },
                },]},
        ],
        model=model,
        # response_format={"type": "json_object", "schema": schema.model_json_schema()},
    )
    #print(extract)
    output = extract.choices[0].message.content
    return output

def idea_from_ads_using_together(text: str , image_url: str , product_name: str) -> str:

    prompt = f'''Analyze the reference advertisement {text} and its image i have provided. For {product_name}, extract the advertising pattern used - like product positioning, overall composition style, text-to-image ratio, announcement style, and promotional approach. Generate a template-style idea that explains how to adapt this advertising pattern for different products while maintaining the same impact.'''
    result = analyze_text_image(prompt,image_url ,AdvertisementIdea)
    return result

def analyze_product_name(product_name: str, company_name: str) -> str:
    """Generates a search keyword based on product name analysis."""
    prompt = f"Generate a short keyword phrase that represents the product: {product_name}. Company name, any adjective or any superlative should not be present in keyword, remove company name {company_name}"
    result = analyze_text(prompt,AnalysisResult)
    return result["keyword"]

def validate_with_together_ai(ad_text, query):
    prompt = f''' Analyze if the following Meta ad text is related to the keyword: {query}

    Ad Text:
    {ad_text}

    Guidelines for analysis:
    1. Check if the text directly mentions the keyword or its close variations
    2. Look for semantic relationships between the text content and the keyword
    3. Consider the context and intended audience of the ad
    4. Analyze if the ad's message or product/service is related to the keyword theme

    Based on the above analysis, determine if the text is relevant to the keyword.
    Provide only a single word response: 'yes' or 'no'

    Response: '''

    response = analyze_text(prompt, RelevanceResponse)
    
    # Here, replace with actual Together AI API call logic
    # For demonstration, let's assume it returns True if ad_text contains the query term.
    return response["is_relevant"]