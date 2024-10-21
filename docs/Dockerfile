FROM mwalbeck/python-poetry
ENV DEBIAN_FRONTEND=noninteractive
ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
RUN --mount=type=cache,target=/var/lib/apt/lists \
      apt update; \
      apt install -y \
        curl \
        make
COPY . /src
WORKDIR /src/docs
RUN python3 -m venv --system-site-packages ${VIRTUAL_ENV} && . ${VIRTUAL_ENV}/bin/activate
RUN make install
