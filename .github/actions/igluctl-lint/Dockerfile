FROM eclipse-temurin:25-jdk-alpine

ARG IGLUCTL_VERSION=0.9.0

RUN apk add --no-cache unzip wget
RUN TMPFILE="$(mktemp)" && \
    wget "https://github.com/snowplow-incubator/igluctl/releases/download/${IGLUCTL_VERSION}/igluctl_${IGLUCTL_VERSION}.zip" -O "$TMPFILE" && \
    unzip -d "$PWD" "$TMPFILE" && \
    rm "$TMPFILE" && \
    chmod u+x igluctl

ENTRYPOINT ["/igluctl", "lint"]
