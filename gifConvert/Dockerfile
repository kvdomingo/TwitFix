FROM public.ecr.aws/lambda/python:3.8 AS builder

RUN yum -y install git curl && yum -y groupinstall 'Development Tools'

RUN git clone https://github.com/kohler/gifsicle

WORKDIR gifsicle

RUN autoreconf -i && ./configure --disable-gifview --disable-gifdiff && make

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

WORKDIR /var/task

RUN git clone https://github.com/ImageOptim/gifski

WORKDIR gifski

RUN /root/.cargo/bin/cargo build --release

FROM public.ecr.aws/lambda/python:3.8

RUN yum -y update && yum -y install git wget tar.x86_64 xz && yum clean all

RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

RUN tar -xvf ffmpeg-release-amd64-static.tar.xz

RUN mv ff*/ffmpeg . && mv ff*/ffprobe . && rm *.tar.xz && rm -rf ff*/

COPY --from=builder /var/task/gifsicle/src/gifsicle ./
COPY --from=builder /var/task/gifski/target/release/gifski ./

# Copy function code
COPY __init__.py ${LAMBDA_TASK_ROOT}/app.py
COPY conv.sh ${LAMBDA_TASK_ROOT}/conv.sh

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.lambda_handler" ] 
