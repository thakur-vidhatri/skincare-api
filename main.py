
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
import requests

app = FastAPI()

class CombinationRequest(BaseModel):
    combinations: Dict[str, List[str]]

def get_skincare_products(chemical_combination):
    url = "https://real-time-amazon-data.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": "feb7423f2cmsh395a274cac68b62p12325cjsn77f572abf16a",
        "X-RapidAPI-Host": "real-time-amazon-data.p.rapidapi.com"
    }

    query_string = ", ".join(chemical_combination) + " skincare"
    querystring = {"query": query_string, "country": "IN"}

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        products = data.get('data', {}).get('products', [])

        if not isinstance(products, list) or not products:
            return ["No products found."]

        formatted_products = []
        for item in products:
            try:
                rating = float(item.get('product_star_rating', 0))
            except:
                rating = 0.0
            try:
                reviews = int(str(item.get('product_num_ratings', '0')).replace(",", ""))
            except:
                reviews = 0
            formatted_products.append(
                {
                    "title": item.get('product_title', 'No Title'),
                    "price": item.get('product_price', 'No Price'),
                    "rating": rating,
                    "reviews": reviews,
                    "link": item.get('product_url', 'No Link'),
                    "image": item.get('product_photo', 'No Image')
                }
            )
        formatted_products.sort(key=lambda x: (x['rating'], x['reviews']), reverse=True)
        return formatted_products[:5]
    else:
        return [f"Failed to fetch data. Status code: {response.status_code}"]

@app.post("/get-products/")
def get_all_products_by_concern(req: CombinationRequest):
    all_results = {}
    for issue, combinations in req.combinations.items():
        top_combination = combinations[:4]
        all_results[issue] = get_skincare_products(top_combination)
    return all_results
