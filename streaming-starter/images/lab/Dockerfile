# Lab: JupyterLab + DuckDB + Postgres/S3 clients + Spark (batch only, local mode).
FROM eclipse-temurin:17-jre AS jre
FROM python:3.10-slim
COPY --from=jre /opt/java/openjdk /opt/java/openjdk
ENV JAVA_HOME=/opt/java/openjdk PATH=/opt/java/openjdk/bin:$PATH
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /work
EXPOSE 8888
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--allow-root", "--ServerApp.token=lab", "--notebook-dir=/work"]
