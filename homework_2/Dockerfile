FROM python:3.12

WORKDIR /homework_2

COPY requirements.txt /homework_2

RUN pip install --upgrade pip && pip install -r /homework_2/requirements.txt

EXPOSE 8080

COPY ./ /homework_2

CMD ["uvicorn", "hw_2:app", "--port", "8080", "--host", "0.0.0.0"]
