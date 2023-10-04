FROM python:3.11

WORKDIR /code

COPY ./ ./

RUN pip install -r requirements.txt
# --no-cache-dir --upgrade 
EXPOSE 5001

ENV PYTHONPATH "${PYTHONPATH}:/front"

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats", "False"]