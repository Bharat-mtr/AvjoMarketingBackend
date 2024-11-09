
from together_ai import analyze_product_name, validate_with_together_ai, idea_from_ads_using_together
from meta_ad_library import search_meta_ads
import requests
import json

def analyze_ads(product_name, company_name):
    keyword = analyze_product_name(product_name, company_name)
    print("Got keyword-> ", keyword)

    # meta_ads = search_meta_ads(keyword)

    # Laoding example json
    with open("exampleJson.json", 'r') as file:
        meta_ads = json.load(file)

    print("Ads from meta are:- ", meta_ads)
    ads = []
    continuation_token = meta_ads.get("continuation_token")
    max_ads = 5
    print("Analysing the ads")

    while len(ads) < max_ads:
        for ad_group in meta_ads.get("results", []):
            for ad in ad_group:
                try:
                    # Ensure 'page_name' does not match the provided company name
                    page_name = ad.get("pageName")
                    if page_name == company_name:
                        continue  # Skip this ad if it matches the company name

                    # Extract images from snapshot
                    snapshot = ad.get("snapshot", {})
                    image_url = None
                    
                    # Check images array
                    images = snapshot.get("images", [])
                    for image in images:
                        image_url = image.get("resized_image_url")
                        if image_url:
                            break
                    
                    # If no image found in images array, check cards array
                    if not image_url:
                        cards = snapshot.get("cards", [])
                        if cards:
                            first_card = cards[0]
                            image_url = first_card.get("resized_image_url")

                    # Skip this ad if no valid image URL is found
                    if not image_url:
                        continue

                    # Extract ad text from body -> markup -> __html
                    body = snapshot.get("body", {})
                    markup = body.get("markup", {})
                    ad_text = markup.get("__html")

                    # Skip this ad if no ad text is present
                    if not ad_text:
                        continue

                    # Send ad text to Together AI for validation
                    if validate_with_together_ai(ad_text, keyword):
                        ads.append({"image_url": image_url, "text": ad_text , "page_name":page_name})
                        print("Got our ", len(ads) , " ad, from company ", page_name)

                        # Stop if we have reached the maximum required ads
                        if len(ads) >= max_ads:
                            break

                except KeyError as e:
                    print(f"Skipping ad due to missing key: {e}")
                    continue  # Skip to the next ad if any required key is missing
            
            # Check if maximum ads are collected
            if len(ads) >= max_ads:
                break

        # If there are no more ads to process or we have collected enough, exit loop
        if len(ads) >= max_ads or not continuation_token:
            break

        # Paginate to next page if necessary
        if continuation_token:
            meta_ads = search_meta_ads(meta_ads["query"], continuation_token)
            continuation_token = meta_ads.get("continuation_token")
            if not meta_ads.get("results"):
                print("Re-fetching data as empty response was returned.")
                meta_ads = search_meta_ads(meta_ads["query"], continuation_token)
    print("json analysis done")
    print("here are ads ", ads)
    return ads

def idea_from_ads(ads : dict, product_name):
    ideas = []

    for ad in ads:
        idea = idea_from_ads_using_together(ad["text"], ad["image_url"], product_name)
        print("idea generated ", idea)
        ideas.append({"ad_text": ad["text"], "image_url": ad["image_url"], "idea":idea})

    return ideas
                        
