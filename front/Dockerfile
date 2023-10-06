FROM python:3.11

WORKDIR /code/front

COPY ./ ./

RUN pip install streamlit
RUN pip install -r requirements.txt
# --no-cache-dir --upgrade 
EXPOSE 5001

ENV PYTHONPATH "${PYTHONPATH}:/code"

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0", "--browser.gatherUsageStats", "False"]