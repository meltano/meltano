ARG BASE_IMAGE=meltano/meltano/base

# build
FROM $BASE_IMAGE as builder
COPY ./ /meltano
WORKDIR /meltano
RUN make sdist

# runtime
FROM $BASE_IMAGE
COPY --from=builder /meltano/dist /meltano/dist
RUN pip install /meltano/dist/meltano-*.tar.gz
RUN rm -rf /meltano
WORKDIR /project

EXPOSE 5000

ENTRYPOINT ["meltano"]
CMD ["ui"]
