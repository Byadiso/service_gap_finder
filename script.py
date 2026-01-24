import time
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_google_maps(niche, location, max_results=10):
    with sync_playwright() as p:
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        search_query = f"{niche} in {location}"
        print(f"🔍 Searching for: {search_query}")
        
        page.goto(f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}")

        # Handle Cookie Consent
        try:
            consent_btn = page.get_by_role("button", name="Zaakceptuj wszystko").or_(page.get_by_role("button", name="Accept all"))
            if consent_btn.is_visible(timeout=5000):
                consent_btn.click()
                print("✅ Cookies accepted.")
        except:
            pass

        print("🖱️ Scrolling sidebar...")
        page.wait_for_selector('a.hfpxzc', timeout=10000)
        for _ in range(2):
            page.mouse.wheel(0, 2000)
            time.sleep(2)

        listings = page.locator('a.hfpxzc').all()
        results = []
        print(f"📋 Found {len(listings)} leads. Analyzing...")

        for i, listing in enumerate(listings[:max_results]):
            try:
                listing.click()
                page.wait_for_timeout(2500) # Give it time to load the right pane

                # --- FIXED SELECTORS ---
                # Use .textContent() to get the string directly
                name = page.locator('h1.DUwDvf').first.text_content() or "Unknown"
                
                # Rating Logic
                rating = "N/A"
                try:
                    # Look for the span that contains the numerical rating (e.g. "4.2")
                    rating_el = page.locator('span.ceNzR').first
                    if rating_el.is_visible():
                        rating_text = rating_el.get_attribute("aria-label") or ""
                        # Extracts "4.5" from "4.5 stars"
                        rating = rating_text.split()[0].replace(",", ".")
                except:
                    pass

                # Website Logic
                website = "None"
                try:
                    website_el = page.locator('a[data-item-id="authority"]').first
                    if website_el.is_visible():
                        website = website_el.get_attribute("href")
                except:
                    pass

                # Phone Logic
                phone = "None"
                try:
                    phone_el = page.locator('button[data-tooltip="Copy phone number"]').or_(page.locator('button[aria-label*="Phone"]')).first
                    if phone_el.is_visible():
                        phone = phone_el.inner_text()
                except:
                    pass

                # Gap Logic
                gap_type = []
                if website == "None": gap_type.append("Needs Website")
                try:
                    if rating != "N/A" and float(rating) < 4.0: gap_type.append("Low Rating")
                except: pass
                if rating == "N/A": gap_type.append("No Reviews")

                results.append({
                    "Name": name.strip(),
                    "Rating": rating,
                    "Website": website,
                    "Phone": phone.strip(),
                    "Service Gap": ", ".join(gap_type) if gap_type else "Fully Optimized"
                })
                print(f"✅ Processed: {name.strip()}")

            except Exception as e:
                print(f"⚠️ Skipping item {i} due to error.")
                continue

        browser.close()
        return results

if __name__ == "__main__":
    data = scrape_google_maps("Plumbers", "Wroclaw")
    
    if data:
        df = pd.DataFrame(data)
        gap_leads = df[df["Service Gap"] != "Fully Optimized"]
        
        if not gap_leads.empty:
            filename = "service_gaps_leads.xlsx"
            gap_leads.to_excel(filename, index=False)
            print(f"\n✅ Done! Saved {len(gap_leads)} leads to {filename}")
            print(gap_leads[["Name", "Service Gap"]])
        else:
            print("✅ All found businesses are already fully optimized!")
    else:
        print("🛑 No data found.")