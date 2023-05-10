from python:3.9

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

ENV PATH "/root/.local/bin:$PATH"

RUN echo $PATH

COPY pyproject.toml poetry.lock poetry.toml ./

RUN poetry install --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "start"]
