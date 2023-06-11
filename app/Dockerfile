FROM python 
WORKDIR /build
COPY requirements.txt /build/requirements.txt

RUN pip install -r /build/requirements.txt
RUN apt-get update
RUN apt-get install -y iputils-ping curl telnet dnsutils vim
RUN apt-get install iptables sudo -y

COPY . /build/app

EXPOSE 26658
EXPOSE 26656
EXPOSE 26657

ENTRYPOINT [ "python3", "/build/app/application_logic.py"]