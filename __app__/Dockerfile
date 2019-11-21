FROM continuumio/miniconda3

# init OS
RUN apt-get update && yes Y | apt-get install build-essential

COPY requirements.txt .

# init Python env
RUN pip install -r requirements.txt

# copy source
COPY *.py ./

CMD ["python3", "main.py"]
