FROM astrocrpublic.azurecr.io/runtime:3.0-11

USER root

# Install Soda Core directly (fast, no scientific package)
# setuptools provides distutils for Python 3.12
RUN pip install --no-cache-dir --default-timeout=300 setuptools && \
    pip install --no-cache-dir --default-timeout=300 soda-core-postgres==3.0.45

USER astro
