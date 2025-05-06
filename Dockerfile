FROM quay.io/jupyter/scipy-notebook:python-3.12

# Install Graphviz
USER root
RUN apt-get update && apt-get install -y graphviz && apt-get clean
RUN apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# Install Poetry
RUN pip install poetry

# Set environment variables to prevent Poetry from creating virtualenvs
ENV POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1


# Set the working directory
WORKDIR /opt/bpmn-python

# Copy the Poetry configuration files
COPY pyproject.toml ./

# Install the dependencies
RUN poetry install --no-root

# Copy the rest of the application code
COPY . .

# Install the application
RUN poetry install

# Expose the port for Jupyter Notebook
EXPOSE 8888

WORKDIR /home/${NB_UID}

CMD [ "start-notebook.py" ]



 