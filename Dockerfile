FROM ubuntu:20.04 AS arsene_wenger
SHELL ["/bin/bash", "-c"]
ENTRYPOINT ["/bin/bash"]

COPY . ./
RUN apt update && \
    apt install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt install -y python3.10 && \
    apt install -y python3.10-venv && \
    cat deb_requirements.txt | xargs -n 1 apt install -y --no-install-recommends

ENV POETRY_HOME='/usr/local' \
    POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3.10 -
RUN poetry --version
RUN ./venvsetup.sh
ENV PYTHONPATH=/
ENV BASH_ENV=/etc/shell_profile
RUN echo "source /activate" > /etc/shell_profile
RUN echo "source /etc/shell_profile" >> /etc/bash.bashrc
# WORKDIR /arseneWenger
# COPY requirements.txt .
# RUN pip install -r requirements.txt

# CMD ["python3", "arsene_wenger/bot.py"]
