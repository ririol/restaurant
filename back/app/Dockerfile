FROM python:3.11

WORKDIR /code/app

COPY ./ ./

RUN pip install aiopg fastapi uvicorn
RUN pip install  -r requirements.txt
# --no-cache-dir --upgrade
EXPOSE 80

ENV PYTHONPATH "${PYTHONPATH}:/code/"

WORKDIR /code/app/src

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80","--reload"]