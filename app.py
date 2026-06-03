import time
import random
import io
import sys
import asyncio
import pandas as pd
import streamlit as st
import plotly.express as px

# FIX: Force Windows to use the Proactor loop policy required by Playwright + Streamlit
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.sync_api import sync_playwright

# --------------------------------------------------
# CONFIG & PREMIUM CSS THEMING
# --------------------------------------------------
st.set_page_config(
    page_title="Rwandan Tourism Lead Workspace", 
    layout="wide", 
    page_icon="🇷🇼"
)

st.markdown("""
<style>
    /* Global layout breathing room */
    .block-container { padding-top: 1.8rem; }
    
    /* Executive Metric Container Stylings */
    div[data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 22px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    div[data-testid="metric-container"] label { 
        color: #94a3b8 !important; 
        font-weight: 600; 
        font-size: 0.95rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { 
        color: #f8fafc; 
        font-size: 1.8rem;
    }
    
    /* Primary CTA Button Overrides */
    .stButton button {
        width: 100%;
        height: 44px;
        border-radius: 8px;
        font-weight: bold;
        background-color: #2563eb;
        color: white;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton button:hover { 
        background-color: #1d4ed8; 
        border: none;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# INITIALIZE SESSION STATES
# --------------------------------------------------
if "scraped_data" not in st.session_state:
    st.session_state.scraped_data = None

# --------------------------------------------------
# SIDEBAR CONTROL INTERFACE
# --------------------------------------------------
st.sidebar.header("🎯 Target Parameters")

available_cities = ["Kigali, Rwanda", "Musanze, Rwanda", "Gisenyi, Rwanda", "Butare, Rwanda"]
available_niches = ["Tour Operator", "Safari Guide", "Boutique Hotel", "Restaurant"]

selected_cities = st.sidebar.multiselect("Target Cities", available_cities, default=[available_cities[0]])
selected_niches = st.sidebar.multiselect("Target Market Niches", available_niches, default=[available_niches[0]])
max_results = st.sidebar.slider("Maximum leads per search route", min_value=5, max_value=50, value=10, step=5)


# --------------------------------------------------
# CORE SCRAPING MODULE
# --------------------------------------------------
def scrape_google_maps(niche, location, page, log_element):
    search_query = f"{niche} in {location}"
    log_element.info(f"🔄 Processing Live Pipeline: **{search_query}**")
    
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
        log_element.warning(f"⚠️ No search index results found for: {search_query}")
        return []

    listings = page.locator('a.hfpxzc').all()
    results = []

    for i, listing in enumerate(listings[:max_results]):
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

            # Smart Qualification Scoring Engine
            score = 0
            gap_type = []
            if website == "None": 
                gap_type.append("Needs Website")
                score += 50
            try:
                if rating != "N/A" and float(rating) < 4.2: 
                    gap_type.append("Reputation Fix")
                    score += 30
            except: pass
            if rating == "N/A": 
                gap_type.append("New/Unrated")
                score += 20

            priority = "Low"
            if score >= 70: priority = "High"
            elif score >= 30: priority = "Medium"

            results.append({
                "City": location.split(",")[0],
                "Category": niche,
                "Business Name": name.strip(),
                "Rating": rating,
                "Website": website,
                "Phone": phone.strip(),
                "Opportunity Score": score,
                "Priority": priority,
                "Service Gap": ", ".join(gap_type) if gap_type else "Fully Optimized"
            })

        except Exception:
            continue

    return results


# --------------------------------------------------
# HEADER SECTION
# --------------------------------------------------
st.title("Rwandan Tourism & Hospitality Lead Workspace")
st.caption("Advanced B2B Discovery Platform engineered for Web Developers, SEO Consultants, and Digital Marketing Agencies.")
st.write("---")


# --------------------------------------------------
# RUNTIME AUTOMATION TRIGGER
# --------------------------------------------------
if st.sidebar.button("🚀 Start Search Automation", use_container_width=True):
    if not selected_cities or not selected_niches:
        st.error("Please configure at least one city and niche target selection.")
    else:
        status_box = st.empty()
        
        # High UI Metrics Row during Live Execution
        metric_container = st.columns(2)
        total_leads_metric = metric_container[0].metric("Total Directory Profiles", "0")
        gap_leads_metric = metric_container[1].metric("Qualified Agency Leads", "0")
        
        table_placeholder = st.empty()
        all_leads = []

        with sync_playwright() as p:
            status_box.info("⚡ Allocating secure browser sandboxes and sandbox elements...")
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            page = context.new_page()

            for city in selected_cities:
                for niche in selected_niches:
                    batch = scrape_google_maps(niche, city, page, status_box)
                    all_leads.extend(batch)
                    
                    if all_leads:
                        current_df = pd.DataFrame(all_leads)
                        current_gap_df = current_df[current_df["Service Gap"] != "Fully Optimized"]
                        
                        total_leads_metric.metric("Total Directory Profiles", len(current_df))
                        gap_leads_metric.metric("Qualified Agency Leads", len(current_gap_df))
                        
                        table_placeholder.dataframe(
                            current_df.sort_values(by="Opportunity Score", ascending=False), 
                            use_container_width=True
                        )
                        
                    time.sleep(random.uniform(1.5, 3))
                time.sleep(1)

            browser.close()
            status_box.success("🏁 Target collection campaign complete! Data stored below.")
            st.session_state.scraped_data = all_leads

# --------------------------------------------------
# PERSISTENT ANALYTICS & LEADS DASHBOARD
# --------------------------------------------------
if st.session_state.scraped_data:
    df_full = pd.DataFrame(st.session_state.scraped_data)
    df_gaps = df_full[df_full["Service Gap"] != "Fully Optimized"]

    # Corporate Analytics Overview
    st.header("📊 Market Insight & Analytics Portal")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Scraped Market Records", len(df_full))
    m2.metric("Targetable Pipeline Gaps", len(df_gaps))
    m3.metric("High Priority Prospects", len(df_gaps[df_gaps["Priority"] == "High"]))
    
    no_web_total = df_gaps["Service Gap"].str.contains("Needs Website").sum()
    m4.metric("Dev Gaps (No Website)", no_web_total)

    # Dynamic Interactive Visualization Charts Row
    st.write("")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        exploded_gaps = df_gaps["Service Gap"].str.split(", ").explode()
        if not exploded_gaps.empty:
            pie_df = exploded_gaps.value_counts().reset_index()
            pie_df.columns = ["Deficiency Type", "Volume"]
            fig_pie = px.pie(
                pie_df, values="Volume", names="Deficiency Type",
                title="Service Gap Market Distributions",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.G10
            )
            fig_pie.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=320)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No service deficiencies detected yet to plot charts.")

    with chart_col2:
        if not df_gaps.empty:
            bar_df = df_gaps["Priority"].value_counts().reset_index()
            bar_df.columns = ["Priority Status", "Count"]
            fig_bar = px.bar(
                bar_df, x="Priority Status", y="Count",
                title="Lead Urgency Prioritization Tiers",
                color="Priority Status",
                color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#10b981"}
            )
            fig_bar.update_layout(margin=dict(t=40, b=10, l=10, r=10), height=320, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

    st.write("---")

    # Segmented Workspace Tab Containers
    tab1, tab2 = st.tabs(["🎯 Pipeline Leads Engine (Gaps Filter)", "📋 Master Directory Base Log"])
    
    with tab1:
        if not df_gaps.empty:
            col_search, col_filter = st.columns([2, 2])
            with col_search:
                search_term = st.text_input("🔍 Live filter pipelines by Business Name...", key="gap_search")
            with col_filter:
                gap_filter = st.multiselect(
                    "Isolate Target Pain Points", 
                    ["Needs Website", "Reputation Fix", "New/Unrated"],
                    default=["Needs Website", "Reputation Fix", "New/Unrated"]
                )
            
            # Apply parameters to DataFrame subset queries
            filtered_gaps = df_gaps[df_gaps["Service Gap"].apply(lambda x: any(g in x for g in gap_filter))]
            if search_term:
                filtered_gaps = filtered_gaps[filtered_gaps["Business Name"].str.contains(search_term, case=False, na=False)]
            
            filtered_gaps_sorted = filtered_gaps.sort_values(by="Opportunity Score", ascending=False)
            st.dataframe(filtered_gaps_sorted, use_container_width=True)
            
            # Spreadsheet Export Engine
            buffer_gaps = io.BytesIO()
            with pd.ExcelWriter(buffer_gaps, engine='openpyxl') as writer:
                filtered_gaps_sorted.to_excel(writer, index=False, sheet_name='Sales Pipeline Targets')
            
            st.download_button(
                label="📥 Export Screened Prospect Sheet (.xlsx)",
                data=buffer_gaps.getvalue(),
                file_name="rwandan_filtered_pipeline.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Outstanding results! Every profile reviewed possesses a robust public configuration.")

    with tab2:
        search_all = st.text_input("🔍 Search Entire Database records...", key="all_search")
        display_full_df = df_full.copy()
        if search_all:
            display_full_df = display_full_df[display_full_df["Business Name"].str.contains(search_all, case=False, na=False)]
        
        st.dataframe(display_full_df, use_container_width=True)
        
        buffer_all = io.BytesIO()
        with pd.ExcelWriter(buffer_all, engine='openpyxl') as writer:
            display_full_df.to_excel(writer, index=False, sheet_name='Complete Master Log')
            
        st.download_button(
            label="📥 Download Master Export Archive (.xlsx)",
            data=buffer_all.getvalue(),
            file_name="rwanda_hospitality_master.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # --------------------------------------------------
    # OUTREACH SALES ASSISTANT CONTEXT FRAMEWORK
    # --------------------------------------------------
    if not df_gaps.empty:
        st.write("---")
        st.header("🎯 Contextual Cold Outreach Generator")
        
        allowed_leads = df_gaps["Business Name"].unique()
        selected_lead = st.selectbox("Select Target Lead Context", allowed_leads)
        lead_data = df_gaps[df_gaps["Business Name"] == selected_lead].iloc[0]
        
        gaps_found = lead_data["Service Gap"]
        phone_num = lead_data["Phone"]
        
        pitch_script = f"Subject: Digital Architecture & Growth Strategy Proposal for {selected_lead}\n\n"
        pitch_script += f"Hi Team at {selected_lead},\n\n"
        pitch_script += f"I came across your profile while reviewing tourism and hospitality operators in {lead_data['City']} and wanted to connect.\n\n"
        
        if "Needs Website" in gaps_found:
            pitch_script += "I noticed that your listing does not currently link out to a direct mobile-responsive website. Since more than 75% of incoming travelers to Rwanda organize itineraries and confirm safari reservations entirely online, establishing an integrated web booking system could capture high-margin bookings directly.\n\n"
        if "Reputation Fix" in gaps_found:
            pitch_script += f"I also noticed your current review baseline sits around a {lead_data['Rating']} star rating. We build automated notification flows that effortlessly nudge satisfied clients to post immediate reviews to your local Google Maps page, improving your search discoverability.\n\n"
            
        pitch_script += "Do you have 5 minutes open for a quick introductory strategy call this week to look over what this could add to your seasonal revenue margins?\n\nBest Regards,\n[Your Professional Name / Agency Title]"
        
        st.text_area("📋 Personalized Cold Outreach Pitch Framework", value=pitch_script, height=230)
        st.info(f"📞 Direct phone contact variable linked: **{phone_num}**")