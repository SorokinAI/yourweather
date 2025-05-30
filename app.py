"""Основной Flask файл с сайтом"""
from flask import Flask, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy
from get_weather import city_weather
from true_data import true_city, today

app = Flask(__name__)

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cities.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class CityStat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    requests = db.Column(db.Integer, default=1)


# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def index():
    # Получаем последний город из cookies или используем "Москва", как самый густонаселённый город в России
    city = request.cookies.get('last_city', 'Москва')

    if request.method == 'POST':
        city = request.form.get('city', city)
        city = true_city(city)  # Нормализация названия

        # Обновляем статистику в БД
        city_record = CityStat.query.filter_by(name=city).first()
        if city_record:
            city_record.requests += 1
        else:
            db.session.add(CityStat(name=city, requests=1))
        db.session.commit()

        # Устанавливаем куки и формируем ответ
        resp = make_response(render_template(
            'index.html',
            weather=city_weather(city),
            city=city,
            date=today,
            top_cities=get_top_cities()
        ))
        resp.set_cookie('last_city', city, max_age=30 * 24 * 60 * 60)
        return resp

    return render_template(
        'index.html',
        weather=city_weather(city),
        city=city,
        date=today,
        top_cities=get_top_cities()
    )


def get_top_cities(limit=5):
    """Возвращает топ-5 городов по количеству запросов"""
    return CityStat.query.order_by(CityStat.requests.desc()).limit(limit).all()


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
