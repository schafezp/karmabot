FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /karmabot
WORKDIR /karmabot
ADD requirements.txt /karmabot/
RUN pip install -r requirements.txt
ADD karmabot /karmabot/karmabot
#WORKDIR /karmabot/karmabot

#CMD [ "python3", "bot.py" ]
WORKDIR /karmabot
CMD [ "python3", "-m", "karmabot.bot" ]