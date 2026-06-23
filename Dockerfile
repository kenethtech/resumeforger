#install dependencies
RUN pip install -r requirements.txt

#copy project files
COPY . .

#export port 10000
Expose 10000

#start flask with Gunicorn
RUN chmod +x start.sh

CMD ["./start.sh"]
