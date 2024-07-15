# Use Amazon Linux 2 as the base image
FROM amazonlinux:2

# Install dependencies
RUN yum install -y \
    unzip \
    zip \
    libX11 \
    GConf2 \
    alsa-lib \
    atk \
    cups-libs \
    gtk3 \
    ipa-gothic-fonts \
    xorg-x11-fonts-Type1 \
    xorg-x11-fonts-misc

# Install Google Chrome
RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm -o /tmp/chrome.rpm && \
    yum install -y /tmp/chrome.rpm && \
    yum clean all

# Install Chromedriver
RUN wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /opt && \
    rm /tmp/chromedriver.zip

# Create symlinks for compatibility
RUN mkdir -p /opt/python/bin
RUN ln -s /usr/bin/google-chrome /opt/python/bin/chromium-browser

# Create the layer zip file
RUN cd /opt && zip -r9 /opt/chromium_layer.zip python chromedriver

# Copy the zip file to the host
CMD cp /opt/chromium_layer.zip /mnt/data
