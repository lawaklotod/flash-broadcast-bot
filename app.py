import os
from flask import Flask

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key')

# Gunakan Railway's provided DATABASE_URL jika ada
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///broadcast.db')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

---

### **STEP 5: Tambah Procfile**

Buat file `Procfile` di root folder:
```
web: gunicorn app:app
```

---

### **STEP 6: Update requirements.txt**
```
flask==3.0.0
flask-cors==4.0.0
python-telegram-bot==20.3
requests==2.31.0
gunicorn==21.2.0
psycopg2-binary==2.9.0
python-dotenv==1.0.0
