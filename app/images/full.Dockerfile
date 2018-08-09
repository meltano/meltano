# -- Is replaced in development branches with the GitLab repo and commit SHA
FROM meltano/meltano:base

# Add extractors to the file
ADD extract /meltano/extract

# -- Clone to get the transformations
RUN git clone https://gitlab.com/meltano/analytics.git /tmp && \
	mv /tmp/elt/dbt /meltano/transformations

# -- Clone default GitLab ML files into /analyze
RUN git clone https://gitlab.com/meltano/looker /meltano/model