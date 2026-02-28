from flask import Flask, render_template, request
import joblib
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Load trained model and vectorizer
model = joblib.load("phishing_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# Trusted brand keywords (works for .com, .in, .co.in etc.)
TRUSTED_KEYWORDS = [
    "amazon",
    "youtube",
    "google",
    "facebook",
    "instagram",
    "microsoft",
    "apple"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""

    if request.method == 'POST':
        url = request.form['url'].strip()

        # 1️⃣ Validate proper URL format
        if not re.match(r'^https?://', url):
            result = "❌ Please enter a valid URL starting with http:// or https://"
            return render_template('index.html', result=result)

        # 2️⃣ Extract domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace("www.", "").lower()

        # 3️⃣ Check trusted brand names
        if any(keyword in domain for keyword in TRUSTED_KEYWORDS):
            result = "✅ Legitimate Website (Recognized Brand)"
            return render_template('index.html', result=result)

        # 4️⃣ ML Prediction for unknown domains
        try:
            url_vector = vectorizer.transform([url])
            prediction = model.predict(url_vector)[0]

            if prediction == 1:
                result = "⚠️ Phishing Website Detected!"
            else:
                result = "✅ Legitimate Website"

        except Exception as e:
            result = "⚠️ Error processing URL. Please try again."

    return render_template('index.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)