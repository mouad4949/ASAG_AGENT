from flask import Flask, render_template, request
import requests
from config import GROQ_API_KEY

app = Flask(__name__)

def corriger_reponse_arabe(text_ar, question, reponse):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    

    prompt = f"""
أنت أستاذ متخصص في اللغة العربية. مهمتك هي تصحيح إجابة طالب عن سؤال حول نص معين.

يرجى تصحيح الإجابة مع مراعاة ما يلي:
1. تصحيح الأخطاء الإملائية والنحوية.
2. تحسين أسلوب الصياغة إن لزم.
3. التأكد من صحة محتوى الإجابة مقارنة بالنص.
4. تقديم تقييم نهائي من 0 إلى 10، مع شرح مفصل للعلامة.

👇 المعلومات:
النص:
{text_ar}

السؤال:
{question}

إجابة الطالب:
{reponse}

✅ من فضلك أعطني النتيجة بالتنسيق التالي (وباللغة العربية فقط):

**الإجابة المصححة:**
...

**الأخطاء المكتشفة:**
1. ...
2. ...
3. ...

**التقييم:**
أعطي هذه الإجابة: ... / 10

**سبب التقييم:**
...
"""

    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    try:
        return result["choices"][0]["message"]["content"]
    except:
        return "❌ خطأ في الاتصال بـ LLM أو في معالجة البيانات."

@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        texte = request.form["texte"]
        question = request.form["question"]
        reponse = request.form["reponse"]
        result = corriger_reponse_arabe(texte, question, reponse)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
