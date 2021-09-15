FROM python:3.9
RUN pip install pipenv
RUN mkdir /c32
WORKDIR /c32
COPY Pipfile* /c32/
RUN pipenv install --system --deploy --ignore-pipfile
ADD links /c32/