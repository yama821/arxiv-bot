FROM python:3
USER root

RUN pip install py-cord
RUN pip install python-dotenv