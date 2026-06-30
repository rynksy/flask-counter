import os
from flask import Flask, render_template_string
from redis import Redis
from .models import db, Counter

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

redis_client = Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Counter</title></head>
<body>
    <h1>Visits: {{ count }}</h1>
</body>
</html>
"""

@app.route('/')
def index():
    counter = Counter.get_counter()
    counter.count += 1
    db.session.commit()
    new_count = counter.count

    redis_client.set('visit_count', new_count)

    return render_template_string(HTML_TEMPLATE, count=new_count)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
