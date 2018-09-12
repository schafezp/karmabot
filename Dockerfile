FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD models.py /code/
ADD postgres_funcs.py /code/
ADD bot.py /code/