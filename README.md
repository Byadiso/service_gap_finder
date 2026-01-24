


# Rwanda Tourism Service-Gap Finder

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/automation-Playwright-green)](https://playwright.dev/python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated **Market Intelligence Engine** designed to identify high-value digital "Service Gaps" in the Rwandan tourism and hospitality sector. This tool audits business profiles across Google Maps to find safari guides, hotels, and restaurants that are losing revenue due to poor digital optimization.



## Project Overview
In the tourism industry, digital trust is the primary currency. This script performs a multi-city audit of the Rwandan market to identify businesses failing the "Digital Trust Test." 

### The "Service Gaps" Identified:
* **The Website Gap:** Businesses with no linked URL, forcing reliance on high-commission third-party platforms.
* **The Reputation Gap:** Operators with ratings below 4.2 who are losing market share to competitors.
* **The Visibility Gap:** New market entrants with zero reviews who require immediate GMB (Google My Business) optimization.

## Features
- **Multi-City Automation:** Seamlessly loops through **Kigali, Musanze, Gisenyi, and Butare**.
- **Multi-Niche Targeting:** Specialized filters for **Tour Operators, Safari Guides, Hotels, and Restaurants**.
- **Smart Gap Detection:** Categorizes leads based on specific business pain points.
- **Data Persistence:** Exports high-quality leads directly to organized Excel spreadsheets.



---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/rwanda-service-gap-finder.git](https://github.com/yourusername/rwanda-service-gap-finder.git)
cd rwanda-service-gap-finder

```

### 2. Install Dependencies

```bash
pip install playwright pandas openpyxl
playwright install chromium

```

### 3. Run the Scraper

```bash
python script.py

```

---

## Data Output

The engine generates a `rwanda_tourism_leads.xlsx` file containing:

| City | Category | Business Name | Rating | Website | Service Gap |
| --- | --- | --- | --- | --- | --- |
| Musanze | Safari Guide | Example Tours | 3.8 | None | Needs Website, Reputation Fix |
| Gisenyi | Boutique Hotel | Lakeside Inn | 4.0 | [Link] | Reputation Fix |

---

## Disclaimer

This project is provided for **educational and research purposes only**.

Scraping Google Maps or other Google services may violate Google's Terms of Service.
The author does not take responsibility for any misuse of this code.

Users are responsible for ensuring their use of this script complies with
all applicable laws, regulations, and third-party terms of service.

## Author

**BYAMUNGU Desire** 

## License

This project is licensed under the MIT License