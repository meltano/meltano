# -- Is replaced in development branches with the GitLab repo and commit SHA
FROM meltano/meltano:base

# Add extractors to the file
ADD extract /extract

# -- Clone to get the transformations
RUN git clone https://gitlab.com/meltano/analytics.git /tmp/transform && \
	mv /tmp/transform /transform

# -- Clone default GitLab ML files into /analyze
RUN git clone https://gitlab.com/meltano/looker /model