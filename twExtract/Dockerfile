FROM public.ecr.aws/lambda/python:3.8
RUN pip install yt-dlp


# Copy function code
COPY __init__.py ${LAMBDA_TASK_ROOT}/app.py

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "app.lambda_handler" ] 
