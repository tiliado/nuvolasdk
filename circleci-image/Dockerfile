FROM fedora

ENV LANG en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN dnf -y update && dnf install -y flatpak && dnf clean all
RUN flatpak remote-add flathub https://dl.flathub.org/repo/flathub.flatpakrepo
RUN flatpak remote-add  nuvola https://dl.tiliado.eu/flatpak/nuvola.flatpakrepo
RUN flatpak install -y nuvola eu.tiliado.NuvolaAdk//stable eu.tiliado.NuvolaAdk//master

ADD ./nuvolasdk-ci /bin
WORKDIR /workdir

CMD ["/bin/nuvolasdk-ci"]
