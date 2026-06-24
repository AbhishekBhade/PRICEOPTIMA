# AI-Powered Competitive Price Tracker

This project is a comprehensive, end-to-end solution designed to help local retail shop owners compete against large-scale e-commerce platforms. By integrating real-time web scraping with a machine learning-based pricing model, the application provides retailers with actionable pricing intelligence.

---

## 1. The Problem
Local electronics retailers face severe challenges due to information asymmetry and "showrooming," where customers visit a physical store to see a product but purchase it online for a lower price. Retailers often struggle with:
* **Manual Inefficiency:** Manually checking competitor websites is logistically impossible for large inventories and results in outdated data.
* **Cost-Prohibitive Tools:** Enterprise-level market intelligence platforms are often too expensive and complex for local retailers.
* **Pricing Uncertainty:** Lacking data-driven insights, retailers often engage in reactive, uninformed price matching that erodes their profit margins.

## 2. Proposed Solution
The "AI-Powered Competitive Price Tracker" is a full-stack, monolithic web application built with **Flask**. It empowers retailers by:
1. **Automating Data Collection:** Using **Selenium**, the system scrapes real-time pricing data from dynamic, JavaScript-heavy e-commerce platforms like Croma and Reliance Digital.
2. **AI-Driven Analysis:** A custom **K-Nearest Neighbors (KNN) Regressor** model, trained on over 14,000 products, analyzes features like category, brand, rating, and review count to calculate a "fair market value" guideline.
3. **Actionable Insights:** The results page presents the lowest current competitor price (the "price to beat") alongside the AI-calculated guideline, enabling informed, data-driven pricing decisions.

## 3. System Architecture & Data Flow
The application follows a streamlined data flow managed by `app.py`:
* **Request:** The user submits a search form via `index.html`.
* **Scraping:** Selenium-controlled bots navigate target sites to extract raw product data, which is then parsed by Beautiful Soup.
* **Processing:** The system identifies the "Best Deal" (lowest price) and prepares the data as a single-row Pandas DataFrame.
* **Prediction:** The Scikit-learn pipeline (including `OneHotEncoder` and `StandardScaler`) processes the data and predicts the optimal price using the KNN algorithm.
* **Display:** Results are rendered dynamically on `results.html`.

## 4. Technical Stack
* **Backend:** Python 3.x, Flask
* **Machine Learning:** Scikit-learn, Pandas, Joblib
* **Web Scraping:** Selenium, Beautiful Soup, Webdriver-Manager
* **Frontend:** HTML5, CSS3

## 5. Performance
The predictive model achieved an **R² score of 0.9948**, demonstrating exceptional accuracy in determining fair market value. Performance was optimized through systematic data cleaning, specifically the removal of sparse, single-item categories, which significantly stabilized the KNN model.

---

## Project Contributors
* **Kapish Kr. Srivastava** ([231b155@juetguna.in](mailto:231b155@juetguna.in))
* **Abhishek Bhade** ([231b006@juetguna.in](mailto:231b006@juetguna.in))
* **Shevya Singh** ([231b310@juetguna.in](mailto:231b310@juetguna.in))
