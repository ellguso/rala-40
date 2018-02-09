FROM python:2.7.13

RUN mkdir /code
WORKDIR /code

COPY requirements.txt .
RUN pip install -r requirements.txt

# RUN pip install asn1crypto==0.22.0
# RUN pip install attrs==17.2.0
# RUN pip install Automat==0.6.0
# RUN pip install backports-abc==0.5
# RUN pip install backports.shutil-get-terminal-size==1.0.0
# RUN pip install BeautifulSoup==3.2.1
# RUN pip install beautifulsoup4==4.6.0
# RUN pip install bleach==2.0.0
# RUN pip install bs4==0.0.1
# RUN pip install certifi==2017.7.27.1
# RUN pip install cffi==1.10.0
# RUN pip install chardet==3.0.4
# RUN pip install configparser==3.5.0
# RUN pip install constantly==15.1.0
# RUN pip install contextlib2==0.5.5
# RUN pip install cryptography==2.0.3
# RUN pip install cssselect==1.0.1
# RUN pip install cycler==0.10.0
# RUN pip install decorator==4.1.2
# RUN pip install entrypoints==0.2.3
# RUN pip install enum34==1.1.6
# RUN pip install flake8==3.4.1
# RUN pip install funcsigs==1.0.2
# RUN pip install functools32==3.2.3.post2
# RUN pip install geoip2==2.5.0
# RUN pip install  html5lib==0.999999999
# RUN pip install  humbledb==5.6.1
# RUN pip install  hyperlink==17.3.0
# RUN pip install  idna==2.5
# RUN pip install  incremental==17.5.0
# RUN pip install  ipaddress==1.0.18
# RUN pip install  ipykernel==4.6.1
# RUN pip install  ipython==5.4.1
# RUN pip install  ipython-genutils==0.2.0
# RUN pip install  ipywidgets==6.0.0
# RUN pip install  jedi==0.10.2
# RUN pip install  Jinja2==2.9.6
# RUN pip install  jsonschema==2.6.0
# RUN pip install  jupyter==1.0.0
# RUN pip install  jupyter-client==5.1.0
# RUN pip install  jupyter-console==5.1.0
# RUN pip install  jupyter-core==4.3.0
# RUN pip install  lxml==3.8.0
# RUN pip install  MarkupSafe==1.0
# RUN pip install  matplotlib==2.0.2
# RUN pip install  maxminddb==1.3.0
# RUN pip install  mccabe==0.6.1
# RUN pip install  mistune==0.7.4
# RUN pip install  mock==2.0.0
# RUN pip install  multiprocessing==2.6.2.1
# RUN pip install  nbconvert==5.2.1
# RUN pip install  nbformat==4.3.0
# RUN pip install  networkx==1.11
# RUN pip install  notebook==5.0.0
# RUN pip install  numpy==1.13.1
# RUN pip install  pandas==0.20.3
# RUN pip install  pandocfilters==1.4.1
# RUN pip install  parsel==1.2.0
# RUN pip install  pathlib2==2.3.0
# RUN pip install  pbr==3.1.1
# RUN pip install  pep8==1.7.0
# RUN pip install  pexpect==4.2.1
# RUN pip install  pickleshare==0.7.4
# RUN pip install  prompt-toolkit==1.0.15
# RUN pip install  ptyprocess==0.5.2
# RUN pip install  py==1.4.34
# RUN pip install  pyasn1==0.3.2
# RUN pip install  pyasn1-modules==0.0.11
# RUN pip install  pycodestyle==2.3.1
# RUN pip install  pyconfig==3.1.1
# RUN pip install  pycparser==2.18
# RUN pip install  PyDispatcher==2.0.5
# RUN pip install  pyflakes==1.5.0
# RUN pip install  Pygments==2.2.0
# RUN pip install  pymongo==3.4.0
# RUN pip install  pyOpenSSL==17.2.0
# RUN pip install  pyparsing==2.2.0
# RUN pip install  pytest==3.2.0
# RUN pip install  python-dateutil==2.6.1
# RUN pip install  pytool==3.4.1
# RUN pip install  pytz==2017.2
# RUN pip install  PyYAML==3.12
# RUN pip install  pyzmq==16.0.2
# RUN pip install  qtconsole==4.3.0
# RUN pip install  queuelib==1.4.2
# RUN pip install  requests==2.18.2
# RUN pip install  ripe.atlas.cousteau==1.4
# RUN pip install  ripe.atlas.sagan==1.2.1
# RUN pip install  scamper-pywarts==0.2.1
# RUN pip install  scandir==1.5
# RUN pip install  scipy==0.19.1
# RUN pip install  Scrapy==1.4.0
# RUN pip install  seaborn==0.8
# RUN pip install  service-identity==17.0.0
# RUN pip install  simplegeneric==0.8.1
# RUN pip install  simplejson==3.11.1
# RUN pip install  singledispatch==3.4.0.3
# RUN pip install  six==1.10.0
# RUN pip install  socketIO-client==0.7.2
# RUN pip install  subprocess32==3.2.7
# RUN pip install  terminado==0.6
# RUN pip install  testpath==0.3.1
# RUN pip install  tornado==4.5.1
# RUN pip install  traitlets==4.3.2
# RUN pip install  Twisted==17.5.0
# RUN pip install  urllib3==1.22
# RUN pip install  vcrpy==1.11.1
# RUN pip install  w3lib==1.18.0
# RUN pip install  wcwidth==0.1.7
# RUN pip install  webencodings==0.5.1
# RUN pip install  websocket-client==0.37.0
# RUN pip install  widgetsnbextension==2.0.0
# RUN pip install  wrapt==1.10.10
# RUN pip install  zope.interface==4.4.3
# RUN pip install  
# 
ADD . /code/

CMD ["jupyter", \
     "notebook",\
     "--no-browser", \
     "--allow-root", \
     "--ip=*", \
     "--NotebookApp.token='1234'"]
