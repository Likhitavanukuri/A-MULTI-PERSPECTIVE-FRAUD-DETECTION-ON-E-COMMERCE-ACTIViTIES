E-commerce platforms are increasingly targeted by fraudulent users who exploit system loopholes through fake transactions, identity theft, or synthetic accounts. 
Traditional fraud detection methods often miss sophisticated attack patterns. 
Our project aims to build a more robust and multi-angle detection model that adapts to evolving fraudulent tactics.
Technologies Used
🔍 Machine Learning & Data Processing
Python: Core language for development
Scikit-learn: ML model training and evaluation
imbalanced-learn: SMOTE and other imbalance handling methods
Pandas / NumPy: Data manipulation
Joblib: Model persistence
🌐 Backend & API
Flask: Lightweight web framework for creating a RESTful API to serve fraud predictions
Requests: For outbound HTTP communication (e.g., Salesforce API from Flask)
📊 Salesforce CRM Integration
Apex Triggers / Flows: To initiate API callouts based on record events
Salesforce REST API: Enables secure bidirectional communication with the fraud detection Flask server
Custom Objects/Fields: Used to store fraud scores and flags in Salesforce records
Lightning Web Components (optional): For visualizing risk insights
📈 Evaluation Tools
Matplotlib / Seaborn: For visualizing data distributions, model performance, and anomalies
🗂️ Infrastructure (Suggested)
Cloud Hosting (Heroku, AWS, GCP): To deploy the Flask app
Salesforce Developer Edition: For testing and integration
