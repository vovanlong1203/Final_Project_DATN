FROM python:3.12.1
EXPOSE 5000
WORKDIR /app

COPY requirements.txt .

# Cài đặt các dependencies từ tệp requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]

# # Set biến môi trường để không hiện thông báo khi cài đặt các dependencies
# ENV PYTHONUNBUFFERED 1

# WORKDIR /app

# COPY requirements.txt .

# # Cài đặt các dependencies từ tệp requirements.txt
# RUN pip install -r requirements.txt

# COPY . .

# ENV FLASK_APP=app.py
# # Expose port mà ứng dụng Flask sẽ chạy
# EXPOSE 5000

# # Khởi chạy Flask app khi container được khởi động
# CMD ["flask", "run", "--host", "0.0.0.0"]