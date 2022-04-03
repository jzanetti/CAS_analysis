FROM amazonlinux:2

ARG DEST_DIR="/opt/case_analysis/"

ADD env_cat_analysis.tar.gz ${DEST_DIR}

ENV PATH="${DEST_DIR}/bin:${PATH}"

RUN yum -y install gzip

WORKDIR ${DEST_DIR}