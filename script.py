import time
import random
import pandas as pd
from playwright.sync_api import sync_playwright

CITIES = ["Kigali, Rwanda", "Musanze, Rwanda", "Gisenyi, Rwanda", "Butare, Rwanda"]
NICHES = ["Tour Operator", "Safari Guide", "Boutique Hotel", "Restaurant"]
MAX_RESULTS_PER_SEARCH = 15

def scrape_google_maps(niche, location, page):
    search_query = f"{niche} in {location}"
    print(f"🔍 Searching for: {search_query}")
    
    page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")

    try:
        consent_btn = page.get_by_role("button", name="Accept all").or_(page.get_by_role("button", name="Zaakceptuj wszystko"))
        if consent_btn.is_visible(timeout=3000):
            consent_btn.click()
    except:
        pass

    try:
        page.wait_for_selector('a.hfpxzc', timeout=8000)
        for _ in range(2):
            page.mouse.wheel(0, 2000)
            time.sleep(1.5)
    except:
        print(f"⚠️ No results found for {search_query}")
        return []

    listings = page.locator('a.hfpxzc').all()
    results = []

    for i, listing in enumerate(listings[:MAX_RESULTS_PER_SEARCH]):
        try:
            listing.click()
            page.wait_for_timeout(2000) 

            
            name = page.locator('h1.DUwDvf').first.text_content() or "Unknown"
            
           
            rating = "N/A"
            rating_el = page.locator('span.ceNzR').first
            if rating_el.is_visible():
                rating_text = rating_el.get_attribute("aria-label") or ""
                rating = rating_text.split()[0].replace(",", ".")

            website = "None"
            website_el = page.locator('a[data-item-id="authority"]').first
            if website_el.is_visible():
                website = website_el.get_attribute("href")

           
            phone = "None"
            phone_el = page.locator('button[data-tooltip="Copy phone number"]').or_(page.locator('button[aria-label*="Phone"]')).first
            if phone_el.is_visible():
                phone = phone_el.inner_text()

            
            gap_type = []
            if website == "None": gap_type.append("Needs Website")
            try:
                if rating != "N/A" and float(rating) < 4.2: gap_type.append("Reputation Fix")
            except: pass
            if rating == "N/A": gap_type.append("New/Unrated")

            results.append({
                "City": location,
                "Category": niche,
                "Name": name.strip(),
                "Rating": rating,
                "Website": website,
                "Phone": phone.strip(),
                "Service Gap": ", ".join(gap_type) if gap_type else "Fully Optimized"
            })
            print(f"✅ Found: {name.strip()} ({niche})")

        except Exception as e:
            continue

    return results


if __name__ == "__main__":
    all_leads = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        for city in CITIES:
            for niche in NICHES:
                print(f"\n--- Starting {niche} in {city} ---")
                batch = scrape_google_maps(niche, city, page)
                all_leads.extend(batch)
                
               
                time.sleep(random.uniform(3, 7))
            
           
            print(f"🏁 Finished {city}. Cooling down...")
            time.sleep(10)

        browser.close()

   
    if all_leads:
        df = pd.DataFrame(all_leads)
       
        gap_leads = df[df["Service Gap"] != "Fully Optimized"]
        
        filename = "rwanda_tourism_leads.xlsx"
        gap_leads.to_excel(filename, index=False)
        print(f"\n🚀 MISSION COMPLETE!")
        print(f"Total leads found: {len(all_leads)}")
        print(f"Businesses needing help: {len(gap_leads)}")
        print(f"File saved: {filename}")