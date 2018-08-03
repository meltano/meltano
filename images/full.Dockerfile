# -- Is replaced in development branches with the GitLab repo and commit SHA
FROM meltano/meltano:base

# -- Clone to get the transformations
RUN git clone https://gitlab.com/meltano/analytics.git /tmp && \
	mv /tmp/elt/dbt /transformations


# -- Clone default GitLab ML files into /analyze
RUN git clone https://gitlab.com/meltano/looker /model