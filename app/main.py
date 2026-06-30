import os
import time
from flask import Flask, render_template_string
from redis import Redis
from .models import db, Counter

app = Flask(__name__)

database_url = os.environ.get('DATABASE_URL')
print(f"Using DATABASE_URL: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
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


def wait_for_db(max_retries=10, delay=3):
    for i in range(max_retries):
        try:
            with app.app_context():
                db.session.execute('SELECT 1')
                print("Database is ready!")
                return
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries} failed: {e}")
            time.sleep(delay)
    raise Exception("Could not connect to database after several retries")


@app.route('/')
def index():
    counter = Counter.get_counter()
    counter.count += 1
    db.session.commit()
    new_count = counter.count

    redis_client.set('visit_count', new_count)

    return render_template_string(HTML_TEMPLATE, count=new_count)


if __name__ == '__main__':
    with app.app_context():
        wait_for_db()
    app.run(host='0.0.0.0', port=5000)